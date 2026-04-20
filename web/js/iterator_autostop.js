import { app } from "/scripts/app.js";
import { api } from "/scripts/api.js";

const STOP_EVENTS = [
    "image_anything_auto_queue_stop_requested",
    "image_anything_iterator_exhausted",
];

let pendingAutoQueueBlocks = 0;
let queuePromptPatched = false;
let toastRoot = null;
let instantRunIteratorMode = false;
let instantRunRequeuePending = false;
let currentExecutionHadError = false;

function graphHasIteratorNodes() {
    const iteratorTypes = new Set(["ImageIterator", "EditDatasetLoader"]);
    const nodes = app?.graph?._nodes ?? [];
    return nodes.some((node) => iteratorTypes.has(node?.type));
}

function isInstantRunActive() {
    return document.querySelector('[data-testid="queue-button"][data-variant="destructive"]') instanceof HTMLElement;
}

function disarmLegacyAutoQueue() {
    if (app?.ui) {
        app.ui.autoQueueEnabled = false;
    }

    const autoQueueCheckbox = document.getElementById("autoQueueCheckbox");
    if (autoQueueCheckbox instanceof HTMLInputElement) {
        autoQueueCheckbox.checked = false;
    }
}

function hasActiveUserGesture() {
    return globalThis.navigator?.userActivation?.isActive === true;
}

function ensureToastRoot() {
    if (toastRoot && document.body.contains(toastRoot)) {
        return toastRoot;
    }

    toastRoot = document.createElement("div");
    toastRoot.className = "image-anything-toast-root";
    Object.assign(toastRoot.style, {
        position: "fixed",
        top: "16px",
        right: "16px",
        zIndex: "10001",
        display: "flex",
        flexDirection: "column",
        gap: "8px",
        pointerEvents: "none",
    });
    document.body.appendChild(toastRoot);
    return toastRoot;
}

function showToast(message, detailText = "") {
    const root = ensureToastRoot();
    const toast = document.createElement("div");

    Object.assign(toast.style, {
        minWidth: "280px",
        maxWidth: "420px",
        padding: "12px 14px",
        borderRadius: "10px",
        border: "1px solid var(--border-color, #4e4e4e)",
        background: "var(--comfy-menu-bg, #353535)",
        color: "var(--fg-color, #fff)",
        boxShadow: "0 10px 24px rgba(0, 0, 0, 0.28)",
        fontSize: "13px",
        lineHeight: "1.45",
        pointerEvents: "auto",
        opacity: "0",
        transform: "translateY(-6px)",
        transition: "opacity 160ms ease, transform 160ms ease",
    });

    const title = document.createElement("div");
    title.textContent = message;
    title.style.fontWeight = "600";
    toast.appendChild(title);

    if (detailText) {
        const detail = document.createElement("div");
        detail.textContent = detailText;
        detail.style.marginTop = "4px";
        detail.style.color = "var(--descrip-text, #b8b8b8)";
        toast.appendChild(detail);
    }

    root.appendChild(toast);

    requestAnimationFrame(() => {
        toast.style.opacity = "1";
        toast.style.transform = "translateY(0)";
    });

    window.setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(-6px)";
        window.setTimeout(() => toast.remove(), 180);
    }, 4200);
}

function disarmInstantRunButton() {
    const queueButton = document.querySelector('[data-testid="queue-button"][data-variant="destructive"]');
    if (!(queueButton instanceof HTMLElement)) {
        return false;
    }

    queueButton.click();
    return true;
}

function stopInstantRunPresentation() {
    let attempts = 0;

    const tryDisarm = () => {
        attempts += 1;
        if (disarmInstantRunButton()) {
            return;
        }

        if (attempts < 12) {
            window.setTimeout(tryDisarm, 120);
        }
    };

    tryDisarm();
}

function buildDetailText(detail) {
    const source = detail?.source ?? "Iterator";
    const totalCount = Number.isFinite(detail?.total_count) ? detail.total_count : null;

    if (source === "ImageIterator" && totalCount !== null) {
        return `Processed ${totalCount} image${totalCount === 1 ? "" : "s"}.`;
    }

    if (source === "EditDatasetLoader" && totalCount !== null) {
        return `Dataset iteration finished after ${totalCount} item${totalCount === 1 ? "" : "s"}.`;
    }

    return "Auto Queue has been stopped for this run.";
}

function patchQueuePrompt() {
    if (queuePromptPatched || typeof app?.queuePrompt !== "function") {
        return;
    }

    const originalQueuePrompt = app.queuePrompt.bind(app);

    app.queuePrompt = async function(number = 0, batchCount = 1, ...rest) {
        const shouldBlockAutoQueue =
            pendingAutoQueueBlocks > 0 &&
            number === 0 &&
            !hasActiveUserGesture();

        if (shouldBlockAutoQueue) {
            pendingAutoQueueBlocks -= 1;
            console.info("[ImageIterator] Blocked one auto-queued prompt after iterator exhaustion.");
            return false;
        }

        if (graphHasIteratorNodes()) {
            instantRunIteratorMode = isInstantRunActive();
        } else {
            instantRunIteratorMode = false;
        }

        return originalQueuePrompt(number, batchCount, ...rest);
    };

    queuePromptPatched = true;
}

patchQueuePrompt();

for (const eventName of STOP_EVENTS) {
    api.addEventListener(eventName, (event) => {
        pendingAutoQueueBlocks += 1;
        instantRunIteratorMode = false;
        instantRunRequeuePending = false;
        currentExecutionHadError = false;
        disarmLegacyAutoQueue();
        stopInstantRunPresentation();

        const detail = event?.detail ?? {};
        showToast(
            "Image Anything iteration finished",
            buildDetailText(detail)
        );
        console.info(
            "[ImageIterator] Exhausted iterator source, stopping auto queue.",
            detail
        );
    });
}

api.addEventListener("execution_start", () => {
    instantRunRequeuePending = false;
    currentExecutionHadError = false;
});

api.addEventListener("execution_error", () => {
    currentExecutionHadError = true;
});

api.addEventListener("executing", async ({ detail }) => {
    if (detail != null) {
        return;
    }

    if (currentExecutionHadError) {
        instantRunIteratorMode = false;
        instantRunRequeuePending = false;
        console.warn("[ImageIterator] Instant Run batch mode stopped after execution_error.");
        return;
    }

    if (!instantRunIteratorMode || instantRunRequeuePending || pendingAutoQueueBlocks > 0) {
        return;
    }

    if (!graphHasIteratorNodes() || !isInstantRunActive()) {
        instantRunIteratorMode = false;
        return;
    }

    instantRunRequeuePending = true;

    window.setTimeout(async () => {
        try {
            if (!instantRunIteratorMode || pendingAutoQueueBlocks > 0) {
                return;
            }

            console.info("[ImageIterator] Instant Run batch mode: queueing next iterator step.");
            await app.queuePrompt(0, 1);
        } catch (error) {
            console.error("[ImageIterator] Failed to queue next instant-run iterator step.", error);
            showToast(
                "Image Anything batch continue failed",
                error instanceof Error ? error.message : "Failed to queue next iteration."
            );
            instantRunIteratorMode = false;
        } finally {
            instantRunRequeuePending = false;
        }
    }, 120);
});
