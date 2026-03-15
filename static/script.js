const API = "http://127.0.0.1:8000"

async function loadTasks() {
    const res = await fetch(API + "/tasks")
    const tasks = await res.json()

    const list = document.getElementById("taskList")
    list.innerHTML = ""

    tasks.forEach(task => {
        const li = document.createElement("li")

        li.innerHTML =
            task.title +
            " <button onclick='deleteTask(" + task.id + ")'>Delete</button>"

        list.appendChild(li)
    })
}

async function addTask() {
    const input = document.getElementById("taskInput")

    await fetch(API + "/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: input.value })
    })

    input.value = ""
    loadTasks()
}

async function deleteTask(id) {
    await fetch(API + "/tasks/" + id, {
        method: "DELETE"
    })

    loadTasks()
}

loadTasks()