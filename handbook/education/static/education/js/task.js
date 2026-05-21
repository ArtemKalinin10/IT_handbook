function animateHintToggle(details, summary, content) {
  if (details.dataset.animating === "true") {
    return;
  }

  const isOpening = !details.open;
  const startHeight = details.offsetHeight;

  if (isOpening) {
    details.open = true;
  }

  const endHeight = isOpening
    ? summary.offsetHeight + content.offsetHeight
    : summary.offsetHeight;

  details.dataset.animating = "true";
  details.classList.add("is-animating");
  details.style.height = `${startHeight}px`;
  details.style.overflow = "hidden";

  requestAnimationFrame(() => {
    details.style.transition = "height 0.3s ease";
    details.style.height = `${endHeight}px`;
  });

  const onTransitionEnd = (event) => {
    if (event.propertyName !== "height") {
      return;
    }

    details.removeEventListener("transitionend", onTransitionEnd);

    if (!isOpening) {
      details.open = false;
    }

    details.style.height = "";
    details.style.transition = "";
    details.style.overflow = "";
    details.dataset.animating = "false";
    details.classList.remove("is-animating");
  };

  details.addEventListener("transitionend", onTransitionEnd);
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".left-tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      const targetId = tab.dataset.tabTarget;
      const targetPanel = targetId ? document.getElementById(targetId) : null;

      if (!targetPanel) {
        return;
      }

      document.querySelectorAll(".left-tab").forEach((item) => {
        item.classList.remove("active");
        item.setAttribute("aria-selected", "false");
      });

      document.querySelectorAll(".left-tab-panel").forEach((panel) => {
        panel.classList.remove("active");
      });

      tab.classList.add("active");
      tab.setAttribute("aria-selected", "true");
      targetPanel.classList.add("active");
    });
  });

  document.querySelectorAll(".hint-block").forEach((details) => {
    const summary = details.querySelector("summary");
    const content = details.querySelector(".hint-content");

    if (!summary || !content) {
      return;
    }

    details.dataset.animating = "false";

    summary.addEventListener("click", (event) => {
      event.preventDefault();
      animateHintToggle(details, summary, content);
    });
  });
});

