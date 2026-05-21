function copyCode(btn) {
  const codeWrapper = btn.closest(".copyable-code-block");
  const codeBlock = codeWrapper ? codeWrapper.querySelector("code") : null;

  if (!codeBlock) {
    return;
  }

  const text = codeBlock.innerText;
  const buttonText = btn.querySelector(".copy-btn-text");

  navigator.clipboard.writeText(text).then(() => {
    if (buttonText) {
      buttonText.innerText = "Скопировано";
    }

    btn.classList.add("copied");

    setTimeout(() => {
      if (buttonText) {
        buttonText.innerText = "Скопировать код";
      }

      btn.classList.remove("copied");
    }, 1500);
  });
}
