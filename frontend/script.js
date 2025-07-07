const BACKEND = "https://todoapp-j13l.onrender.com";
const listEl = document.getElementById("task-list");
const inputEl = document.getElementById("task-input");
const addBtn = document.getElementById("add-btn") || null;
let tasks = [];
let filter = "all";

// Fetch tasks from backend
async function fetchTasks() {
  const res = await fetch(`${BACKEND}/tasks`);
  tasks = await res.json();
  renderTasks();
}

// Send chat message -> tasks
async function sendPrompt() {
  const msg = inputEl.value.trim();
  if (!msg) return;

  const sendBtn = document.getElementById("send-btn");
  const spinner = document.getElementById("loading");

  // Show loading spinner
  sendBtn.classList.add("hidden");
  spinner.classList.remove("hidden");

  try {
    await fetch(`${BACKEND}/chat?message=${encodeURIComponent(msg)}`, { method: 'POST' });
    inputEl.value = "";
    await fetchTasks();
  } catch (err) {
    alert("Failed to add task");
  }

  // Hide spinner and show send icon again
  sendBtn.classList.remove("hidden");
  spinner.classList.add("hidden");
}


// Delete task
async function deleteTask(id) {
  await fetch(`${BACKEND}/tasks/${id}`, { method: "DELETE" });
  await fetchTasks();
}

// Checkbox toggle (mark done locally only)
function toggleDone(idx) {
  tasks[idx].is_done = !tasks[idx].is_done;
  renderTasks();
}

// Clear completed
async function clearCompleted() {
  const completedTasks = tasks.filter(t => t.is_done);
  for (const task of completedTasks) {
    await fetch(`${BACKEND}/tasks/${task.id}`, { method: "DELETE" });
  }
  await fetchTasks(); // Refresh task list after deletion
}


// Filtering
function applyFilter() {
  document.querySelectorAll(".filter button")
    .forEach(btn => btn.classList.toggle("active", btn.id === filter));
  renderTasks();
}

// Drag & Drop
let dragSrcIdx = null;

function dragStart(e) { dragSrcIdx = +this.dataset.index; }
function drop(e) {
  const dst = +this.dataset.index;
  tasks.splice(dst, 0, tasks.splice(dragSrcIdx, 1)[0]);
  renderTasks();
}

function renderTasks() {
  const filtered = tasks.filter((t) =>
    filter === "all" ||
    (filter === "active" && !t.is_done) ||
    (filter === "completed" && t.is_done)
  );

  listEl.innerHTML = "";

  filtered.forEach((t, i) => {
    const li = document.createElement("li");
    li.className = "card todo-item";
    li.dataset.index = i;

    li.innerHTML = `
      <div class="todo">
        <input type="checkbox" id="c${i}" ${t.is_done ? "checked" : ""}>
        <label for="c${i}"></label>
        <p>${t.title}</p>
      </div>
      <div class="icons">
        <i class="fa fa-times"></i>
      </div>`;

    // Events
    li.querySelector("input").addEventListener("change", () => toggleDone(i));
    li.querySelector(".fa-times").addEventListener("click", () => deleteTask(t.id));
   
    
    listEl.appendChild(li);
  });

  document.getElementById("items-left").textContent = tasks.filter(t => !t.is_done).length;
}

// Event bindings
if (addBtn) addBtn.addEventListener("click", sendPrompt);
inputEl.addEventListener("keypress", e => e.key === "Enter" && sendPrompt());
document.getElementById("send-btn").addEventListener("click", sendPrompt);


document.getElementById("all").onclick = () => (filter = "all", applyFilter());
document.getElementById("active").onclick = () => (filter = "active", applyFilter());
document.getElementById("completed").onclick = () => (filter = "completed", applyFilter());
document.getElementById("clear").addEventListener("click", clearCompleted);

// Initial load
fetchTasks();
