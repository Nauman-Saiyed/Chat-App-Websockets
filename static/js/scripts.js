let socket = null;
let roomId = null;
let isAdmin = false;

/* =========================
   LOGIN
========================= */
$("#login-btn").click(async () => {
  const res = await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: $("#username").val(),
      password: $("#password").val()
    })
  });

  const data = await res.json();
  if (!res.ok) return alert(data.detail || "Login failed");

  localStorage.setItem("token", data.access_token);

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

  connectSocket();
}

/* =========================
   WEBSOCKET
========================= */
function connectSocket() {
  socket = new WebSocket(
    `ws://${location.host}/message?room=${roomId}&token=${localStorage.getItem("token")}`
  );

  socket.onmessage = (e) => {
    const msg = JSON.parse(e.data);

    /* 🔥 ROOM CLOSED BY ADMIN */
    if (msg.type === "ROOM_CLOSED") {
      alert("Room closed by admin");
      socket.close();
      resetLobby();
      return;
    }

    /* 🔥 USER LEFT */
    if (msg.type === "USER_LEFT") {
      $("#messages").append(
        $("<li>").addClass("system").text(`${msg.username} left the room`)
      );
      return;
    }

    /* 🔥 NORMAL CHAT MESSAGE */
    $("#messages").append(
      $("<li>").text(`${msg.username}: ${msg.message}`)
    );
  };

  socket.onclose = () => {
    // ❌ NO GUESSING HERE
    console.log("Socket closed");
  };
}

/* =========================
   SEND MESSAGE
========================= */
$("#send").click(() => {
  const msg = $("#message").val();
  if (!msg || !socket) return;

  socket.send(
    JSON.stringify({
      message: msg,
      room: roomId
    })
  );

  $("#message").val("");
});

/* =========================
   LEAVE ROOM
========================= */
$("#leave-room").click(async () => {
  await fetch("/rooms/leave", {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ room_id: roomId })
  });

  if (socket) socket.close();
  resetLobby();
});

/* =========================
   HELPERS
========================= */
function resetLobby() {
  roomId = null;
  isAdmin = false;
  socket = null;

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
