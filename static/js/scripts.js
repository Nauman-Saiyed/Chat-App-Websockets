let socket = null;
let roomId = null;
let isAdmin = false;

// track current user and members state
let currentUsername = localStorage.getItem("username") || null;
let members = []; // array of { username: string, active: boolean }

// stable per-browser id (so your backend user_id is not empty)
let clientId = localStorage.getItem("clientId");
if (!clientId) {
  clientId = (crypto && crypto.randomUUID) ? crypto.randomUUID() : String(Date.now());
  localStorage.setItem("clientId", clientId);
}

/* =========================
   LOGIN
========================= */
$("#login-btn").click(async () => {
  const username = $("#username").val();
  const password = $("#password").val();

  const res = await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();
  if (!res.ok) return alert(data.detail || "Login failed");

  localStorage.setItem("token", data.access_token);

  currentUsername = username;
  localStorage.setItem("username", username);

  $("#login-section").hide();
  $("#lobby-section").show();
});

/* =========================
   CREATE ROOM
========================= */
$("#create-room").click(async () => {
  const roomName = $("#new-room-name").val();
  if (!roomName) return alert("Room name required");

  const res = await fetch("/rooms", {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ room_name: roomName })
  });

  const data = await res.json();
  if (!res.ok) return alert(data.detail);

  roomId = data.room_id;
  isAdmin = true;

  enterRoom(data.room_name);
});

/* =========================
   JOIN ROOM
========================= */
$("#join-room").click(async () => {
  const joinId = $("#join-room-id").val();
  if (!joinId) return alert("Room ID required");

  const res = await fetch("/rooms/join", {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ room_id: joinId })
  });

  const data = await res.json();
  if (!res.ok) return alert(data.detail);

  roomId = data.room_id;
  isAdmin = data.is_admin;

  enterRoom(data.room_name);
});

/* =========================
   ENTER ROOM
========================= */
function enterRoom(roomName) {
  $("#lobby-section").hide();
  $("#chat-section").show();

  $("#room-name").text(roomName);
  $("#room-id").text(roomId);

  $("#current-user").text(currentUsername || "-");

  $("#messages").empty();
  members = [];
  renderMembers();

  connectSocket();
}

/* =========================
   WEBSOCKET
========================= */
function connectSocket() {
  // IMPORTANT: your backend is /ws/{room_id}
  // and it reads query params user_id & username
  socket = new WebSocket(
    `ws://${location.host}/ws/${roomId}?user_id=${encodeURIComponent(clientId)}&username=${encodeURIComponent(currentUsername || "")}`
  );

  socket.onopen = () => {
    console.log("Socket connected:", roomId);
    // DO NOT send HELLO / LEAVE here (backend doesn't handle them)
  };

  socket.onmessage = (e) => {
    let msg;
    try {
      msg = JSON.parse(e.data);
    } catch {
      console.log("Non-JSON message:", e.data);
      return;
    }

    if (Array.isArray(msg.room_members)) {
      setMembersFromBackend(msg.room_members);
    }

    // JOINED
    if (msg.type === "user_joined") {
      markUserActive(msg.username, true);
      $("#messages").append(
        $("<li>").addClass("system").text(`${msg.username} has joined`)
      );
      scrollMessagesToBottom();
      return;
    }

    // LEFT
    if (msg.type === "user_left") {
      markUserActive(msg.username, true);
      $("#messages").append(
        $("<li>").addClass("system").text(`${msg.username} left the room`)
      );
      scrollMessagesToBottom();
      return;
    }

    // CHAT
    if (msg.type === "chat_message") {
      $("#messages").append(
        $("<li>").text(`${msg.username}: ${msg.message}`)
      );
      scrollMessagesToBottom();
      return;
    }

    // TYPING (optional: ignore or implement later)
    if (msg.type === "typing") {
      return;
    }

    console.log("WS MSG:", msg);
  };

  socket.onclose = () => {
    console.log("Socket closed");
  };

  socket.onerror = (err) => {
    console.log("Socket error:", err);
  };
}

/* =========================
   SEND MESSAGE
========================= */
$("#send").click(() => {
  const msg = $("#message").val();
  if (!msg || !socket || socket.readyState !== WebSocket.OPEN) return;

  // backend expects: { type:"chat_message", message:"..." }
  socket.send(
    JSON.stringify({
      type: "chat_message",
      message: msg
    })
  );

  $("#message").val("");
});

$("#message").on("keypress", (e) => {
  if (e.which === 13) $("#send").click();
});

/* =========================
   LEAVE ROOM
========================= */
$("#leave-room").click(async () => {
  // HTTP leave route (your backend already has it)
  await fetch("/rooms/leave", {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ room_id: roomId })
  });

  // Do NOT send LEAVE over websocket (backend doesn't handle it)
  if (socket) socket.close();
  resetLobby();
});

/* =========================
   MEMBERS UI HELPERS
========================= */
// Your backend sends: room_members: ["a","b","c"]
function setMembersFromBackend(members) {
  $("#members").empty();
  members.forEach(m => {
    $("#members").append($("<li>").text(`${m.username} (${m.user_id})`));
  });
  $("#member-count").text(members.length);
}


function renderMembers() {
  const $list = $("#members-list");
  $list.empty();

  for (const m of members) {
    const $li = $("<li>");
    const $dot = $("<span>").addClass("dot").toggleClass("active", !!m.active);
    const $name = $("<span>").addClass("member-name").text(m.username);
    $li.append($dot, $name);
    $list.append($li);
  }

  $("#user-count").text(members.length);
}

/* =========================
   HELPERS
========================= */
function resetLobby() {
  roomId = null;
  isAdmin = false;
  socket = null;

  members = [];
  $("#members-list").empty();
  $("#user-count").text("0");

  $("#messages").empty();
  $("#chat-section").hide();
  $("#lobby-section").show();
}

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + localStorage.getItem("token")
  };
}

function scrollMessagesToBottom() {
  const el = document.getElementById("messages");
  if (el) el.scrollTop = el.scrollHeight;
}
