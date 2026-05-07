const state = {
    token: localStorage.getItem("hotelToken") || "",
    user: JSON.parse(localStorage.getItem("hotelUser") || "null"),
    hotels: [],
};

const els = {
    sessionStatus: document.querySelector("#sessionStatus"),
    logoutButton: document.querySelector("#logoutButton"),
    notice: document.querySelector("#notice"),
    hotelsGrid: document.querySelector("#hotelsGrid"),
    hotelTemplate: document.querySelector("#hotelTemplate"),
    roomTemplate: document.querySelector("#roomTemplate"),
    bookingTemplate: document.querySelector("#bookingTemplate"),
    loginForm: document.querySelector("#loginForm"),
    registerForm: document.querySelector("#registerForm"),
    filterForm: document.querySelector("#filterForm"),
    hotelForm: document.querySelector("#hotelForm"),
    refreshButton: document.querySelector("#refreshButton"),
    refreshBookingsButton: document.querySelector("#refreshBookingsButton"),
    profileCard: document.querySelector("#profileCard"),
    bookingsList: document.querySelector("#bookingsList"),
};

function headers(json = true) {
    const result = {};
    if (json) result["Content-Type"] = "application/json";
    if (state.token) result.Authorization = `Bearer ${state.token}`;
    return result;
}

function showNotice(message, isError = true) {
    if (!els.notice) return;
    els.notice.textContent = readableError(message);
    els.notice.classList.remove("hidden");
    els.notice.style.background = isError ? "#fff7ed" : "#ecfdf5";
    els.notice.style.color = isError ? "#8a4b12" : "#065f46";
    window.clearTimeout(showNotice.timer);
    showNotice.timer = window.setTimeout(() => els.notice.classList.add("hidden"), 4500);
}

function readableError(message) {
    try {
        const data = JSON.parse(message);
        if (Array.isArray(data)) return data.join(" ");
        if (data.detail) return data.detail;
        if (data.non_field_errors) return data.non_field_errors.join(" ");
        return Object.entries(data)
            .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(" ") : value}`)
            .join(" ");
    } catch {
        return message;
    }
}

async function api(path, options = {}) {
    const response = await fetch(path, options);
    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json") ? await response.json() : await response.text();

    if (!response.ok) {
        const message = typeof data === "string" ? data : JSON.stringify(data);
        throw new Error(message);
    }

    return data;
}

function saveSession(payload) {
    state.token = payload.token;
    state.user = payload.user;
    localStorage.setItem("hotelToken", state.token);
    localStorage.setItem("hotelUser", JSON.stringify(state.user));
    renderSession();
}

function clearSession() {
    state.token = "";
    state.user = null;
    localStorage.removeItem("hotelToken");
    localStorage.removeItem("hotelUser");
    renderSession();
    renderCabinet();
}

function renderSession() {
    if (!els.sessionStatus || !els.logoutButton) return;
    if (state.user) {
        els.sessionStatus.textContent = state.user.email;
        els.logoutButton.classList.remove("hidden");
        return;
    }

    els.sessionStatus.textContent = "Гость";
    els.logoutButton.classList.add("hidden");
}

function formToJson(form) {
    return Object.fromEntries(new FormData(form).entries());
}

function resetForm(form) {
    form.reset();
    syncFileLabels(form);
}

function syncFileLabels(root = document) {
    root.querySelectorAll('input[type="file"]').forEach((input) => {
        const label = input.closest("label")?.querySelector(".file-name");
        if (!label) return;
        label.textContent = input.files.length ? input.files[0].name : "Файл не выбран";
    });
}

function setupFileControls(root = document) {
    root.querySelectorAll('input[type="file"]').forEach((input) => {
        input.addEventListener("change", () => syncFileLabels(input.closest("label") || document));
    });

    root.querySelectorAll(".file-clear").forEach((button) => {
        button.addEventListener("click", () => {
            const label = button.closest("label");
            const input = label?.querySelector('input[type="file"]');
            if (!input) return;
            input.value = "";
            syncFileLabels(label);
        });
    });
}

function setAuthTab(tab) {
    document.querySelectorAll("[data-auth-tab]").forEach((button) => {
        button.classList.toggle("active", button.dataset.authTab === tab);
    });
    els.loginForm?.classList.toggle("hidden", tab !== "login");
    els.registerForm?.classList.toggle("hidden", tab !== "register");
}

function hotelQuery() {
    const params = new URLSearchParams();
    if (!els.filterForm) return "/api/hotels/";

    const data = new FormData(els.filterForm);
    for (const [key, value] of data.entries()) {
        if (value) params.set(key, value);
    }
    return params.toString() ? `/api/hotels/?${params}` : "/api/hotels/";
}

async function loadHotels() {
    if (!els.hotelsGrid) return;
    els.hotelsGrid.innerHTML = '<p class="empty">Загружаю отели...</p>';
    state.hotels = await api(hotelQuery());
    renderHotels();
}

async function loadHotelDetails(id) {
    return api(`/api/hotels/${id}/`);
}

function renderHotels() {
    if (!els.hotelsGrid || !els.hotelTemplate) return;
    els.hotelsGrid.innerHTML = "";

    if (!state.hotels.length) {
        els.hotelsGrid.innerHTML = '<p class="empty">Отелей по этим условиям пока нет.</p>';
        return;
    }

    state.hotels.forEach((hotel) => {
        const node = els.hotelTemplate.content.firstElementChild.cloneNode(true);
        const image = node.querySelector(".hotel-image");
        const title = node.querySelector("h3");
        const address = node.querySelector(".address");
        const description = node.querySelector(".description");
        const rating = node.querySelector(".rating");
        const rooms = node.querySelector(".rooms");

        if (hotel.hostel_images) image.src = hotel.hostel_images;
        image.alt = hotel.title;
        title.textContent = hotel.title;
        address.textContent = hotel.address;
        description.textContent = hotel.description;
        rating.textContent = Number(hotel.rating || 0).toFixed(1);

        rooms.innerHTML = '<p class="empty">Открываю номера...</p>';
        loadHotelDetails(hotel.id)
            .then((details) => renderRooms(rooms, details.rooms || []))
            .catch((error) => {
                rooms.innerHTML = `<p class="empty">${readableError(error.message)}</p>`;
            });

        node.querySelector(".room-form")?.addEventListener("submit", (event) => createRoom(event, hotel.id));
        node.querySelector(".review-form")?.addEventListener("submit", (event) => createReview(event, hotel.id));
        setupFileControls(node);
        els.hotelsGrid.appendChild(node);
    });
}

function renderRooms(container, rooms) {
    container.innerHTML = "";

    if (!rooms.length) {
        container.innerHTML = '<p class="empty">Номеров пока нет.</p>';
        return;
    }

    rooms.forEach((room) => {
        const node = els.roomTemplate.content.firstElementChild.cloneNode(true);
        const image = node.querySelector("img");
        const name = node.querySelector("strong");
        const meta = node.querySelector("span");

        if (room.room_images) image.src = room.room_images;
        image.alt = room.type;
        name.textContent = room.type === "deluxe" ? "Люкс" : "Стандартный";
        meta.textContent = `${room.price_on_one_day} за сутки`;
        node.querySelector(".booking-form").addEventListener("submit", (event) => createBooking(event, room.id));
        container.appendChild(node);
    });
}

async function login(event) {
    event.preventDefault();
    const payload = await api("/api/auth/login/", {
        method: "POST",
        headers: headers(),
        body: JSON.stringify(formToJson(event.currentTarget)),
    });
    saveSession(payload);
    resetForm(event.currentTarget);
    showNotice("Вы вошли в систему.", false);
}

async function register(event) {
    event.preventDefault();
    const payload = await api("/api/auth/register/", {
        method: "POST",
        headers: headers(),
        body: JSON.stringify(formToJson(event.currentTarget)),
    });
    saveSession(payload);
    resetForm(event.currentTarget);
    showNotice("Аккаунт создан.", false);
}

async function createHotel(event) {
    event.preventDefault();
    if (!state.token) {
        showNotice("Сначала войдите в аккаунт.");
        return;
    }

    await api("/api/hotels/", {
        method: "POST",
        headers: headers(false),
        body: new FormData(event.currentTarget),
    });
    resetForm(event.currentTarget);
    showNotice("Отель добавлен.", false);
}

async function createRoom(event, hotelId) {
    event.preventDefault();
    if (!state.token) {
        showNotice("Сначала войдите в аккаунт.");
        return;
    }

    const data = new FormData(event.currentTarget);
    data.set("hotel", hotelId);

    await api("/api/rooms/", {
        method: "POST",
        headers: headers(false),
        body: data,
    });
    resetForm(event.currentTarget);
    showNotice("Номер добавлен.", false);
    await loadHotels();
}

async function createBooking(event, roomId) {
    event.preventDefault();
    if (!state.token) {
        showNotice("Сначала войдите в аккаунт.");
        return;
    }

    const data = formToJson(event.currentTarget);
    data.room = roomId;

    const booking = await api("/api/bookings/", {
        method: "POST",
        headers: headers(),
        body: JSON.stringify(data),
    });
    resetForm(event.currentTarget);
    showNotice(`Бронь создана. Итоговая цена: ${booking.total_price}`, false);
}

async function createReview(event, hotelId) {
    event.preventDefault();
    if (!state.token) {
        showNotice("Сначала войдите в аккаунт.");
        return;
    }

    const data = formToJson(event.currentTarget);
    data.hotel = hotelId;

    await api("/api/reviews/", {
        method: "POST",
        headers: headers(),
        body: JSON.stringify(data),
    });
    resetForm(event.currentTarget);
    showNotice("Отзыв опубликован.", false);
    await loadHotels();
}

async function loadCabinet() {
    if (!els.profileCard && !els.bookingsList) return;
    renderCabinet();

    if (!state.token) return;

    const [profile, bookings] = await Promise.all([
        api("/api/auth/me/", { headers: headers(false) }),
        api("/api/bookings/my/", { headers: headers(false) }),
    ]);
    state.user = { ...state.user, ...profile };
    localStorage.setItem("hotelUser", JSON.stringify(state.user));
    renderSession();
    renderProfile(profile);
    renderBookings(bookings);
}

function renderCabinet() {
    if (els.profileCard && !state.token) {
        els.profileCard.innerHTML = '<p class="empty">Войдите, чтобы увидеть данные профиля.</p>';
    }
    if (els.bookingsList && !state.token) {
        els.bookingsList.innerHTML = '<p class="empty">Брони появятся после входа.</p>';
    }
}

function renderProfile(profile) {
    if (!els.profileCard) return;
    els.profileCard.innerHTML = `
        <dl>
            <div><dt>Email</dt><dd>${profile.email}</dd></div>
            <div><dt>ФИО</dt><dd>${profile.full_name}</dd></div>
            <div><dt>Телефон</dt><dd>${profile.phone}</dd></div>
        </dl>
    `;
}

function renderBookings(bookings) {
    if (!els.bookingsList || !els.bookingTemplate) return;
    els.bookingsList.innerHTML = "";

    if (!bookings.length) {
        els.bookingsList.innerHTML = '<p class="empty">У вас пока нет бронирований.</p>';
        return;
    }

    bookings.forEach((booking) => {
        const node = els.bookingTemplate.content.firstElementChild.cloneNode(true);
        node.querySelector("strong").textContent = `Бронь ${booking.id}`;
        node.querySelector("span").textContent = `${booking.check_in} - ${booking.check_out}`;
        node.querySelector("b").textContent = `${booking.total_price}`;
        els.bookingsList.appendChild(node);
    });
}

document.querySelectorAll("[data-auth-tab]").forEach((button) => {
    button.addEventListener("click", () => setAuthTab(button.dataset.authTab));
});

els.loginForm?.addEventListener("submit", (event) => login(event).catch((error) => showNotice(error.message)));
els.registerForm?.addEventListener("submit", (event) => register(event).catch((error) => showNotice(error.message)));
els.hotelForm?.addEventListener("submit", (event) => createHotel(event).catch((error) => showNotice(error.message)));
els.filterForm?.addEventListener("submit", (event) => {
    event.preventDefault();
    loadHotels().catch((error) => showNotice(error.message));
});
els.refreshButton?.addEventListener("click", () => loadHotels().catch((error) => showNotice(error.message)));
els.refreshBookingsButton?.addEventListener("click", () => loadCabinet().catch((error) => showNotice(error.message)));
els.logoutButton?.addEventListener("click", () => {
    clearSession();
    showNotice("Вы вышли из аккаунта.", false);
});

renderSession();
setupFileControls();
loadHotels().catch((error) => showNotice(error.message));
loadCabinet().catch((error) => showNotice(error.message));
