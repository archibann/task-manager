const API = ""

async function toggleComplete(id, completed) {
    await fetch(API + "/tasks/" + id + "/complete", {
        method: "PUT"
    });
    loadTasks();
}

async function loadTasks() {
    const res = await fetch(API + "/tasks")
    const tasks = await res.json()

    const list = document.getElementById("taskList")
    list.innerHTML = ""

    tasks.forEach(task => {
        const li = document.createElement("li")

        li.innerHTML =
            task.title + 
            (task.deadline ? " (Deadline: " + task.deadline + ")" : "") +
            (task.priority ? " [Priority: " + task.priority + "]" : "") +
            " <button onclick='deleteTask(" + task.id + ")'>Delete</button>" +
            " <button onclick='toggleComplete(" + task.id + ", " + task.completed + ")'>" +
            (task.completed ? "Undo" : "Complete") + "</button>"+
            " <button onclick='editTask(" + task.id + ")'>Edit</button>";

        list.appendChild(li)
    })
}

async function addTask() {
    const input = document.getElementById("taskInput")
    const deadline = document.getElementById("taskDeadline").value || null
    const priority = document.getElementById("taskPriority").value || null

    await fetch(API + "/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
             title: input.value,
             deadline: deadline,
             priority: priority
        })
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