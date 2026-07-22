
document.addEventListener("DOMContentLoaded", () => {
    const taskId = document.body.dataset.taskId;
    const socket = new WebSocket(
        `ws://${window.location.host}/ws/task/${taskId}/`,
    );

    socket.onmessage = function (event) {
        const data = JSON.parse(event.data);

        const el = document.getElementById(
        `submission-${data.submission_id}`,
        );

        if (el) {
            el.classList.remove("pending", "accepted", "wrong");

            if (data.status === "done") {
                el.classList.add("accepted");
                el.innerText = "Решение зачтено OK";
            }

            if (data.status === "failed") {
                el.classList.add("wrong");
                el.innerText = "Неправильный ответ WA";
            }
        }
    };
});
