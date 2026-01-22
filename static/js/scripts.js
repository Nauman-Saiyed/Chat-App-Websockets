let socket = null;
let room = "";

/* =========================
   LOGIN (AUTO CREATE USER)
========================= */

$("#login-btn").click(async function () {
  const username = $("#login-username").val();
  const password = $("#login-password").val();

  if (!username || !password) {
    alert("Username and password are required");
    return;
  }

  try {
    const response = await fetch("/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        username: username,
        password: password
      })
    });

    const data = await response.json();

    if (!response.ok) {
      alert(data.detail || "Login failed");
      return;
    }

    // Store JWT
    localStorage.setItem("access_token", data.access_token);

    // Move to room section
    $("#auth-section").hide();
    $("#room-section").show();

  } catch (error) {
    console.error(error);
    alert("Server not reachable");
  }
});

/* =========================
   JOIN ROOM
========================= */

$("#join-room").click(function () {
  room = $("#room-name").val();

  if (!room) {
    alert("Enter a room name");
    return;
  }

  $("#room-section").hide();
  $("#chat").show();
  $("#message-input").show();

  initializeWebSocket();
});

/* =========================
   WEBSOCKET
========================= */

function initializeWebSocket() {
  const token = localStorage.getItem("access_token");

  if (!token) {
    alert("Unauthorized");
    return;
  }

  socket = new WebSocket(
    `ws://${location.host}/message?room=${room}&token=${token}`
  );

  socket.onopen = function () {
    console.log("WebSocket connected");
  };

  socket.onmessage = function (event) {
    const data = JSON.parse(event.data);

    const msgClass = data.isMe ? "user-message" : "other-message";
    const messageElement = $("<li>")
      .addClass(msgClass)
      .text(`${data.username}: ${data.data}`);

    $("#messages").append(messageElement);
    $("#chat").scrollTop($("#chat")[0].scrollHeight);
  };

  socket.onerror = function () {
    alert("WebSocket error");
  };

  socket.onclose = function () {
    alert("WebSocket disconnected");
  };
}

/* =========================
   SEND MESSAGE
========================= */

$("#send").click(sendMessage);

$("#message").keydown(function (e) {
  if (e.key === "Enter") {
    sendMessage();
  }
});

function sendMessage() {
  const message = $("#message").val();

  if (!message || !socket) return;

  socket.send(
    JSON.stringify({
      message: message,
      room: room
    })
  );

  $("#message").val("");
}

/* =========================
   LOGOUT (OPTIONAL)
========================= */

function logout() {
  localStorage.removeItem("access_token");
  if (socket) socket.close();
  location.reload();
}
