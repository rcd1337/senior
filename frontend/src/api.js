const API_URL = "http://localhost:8000/api/v1";

export function getToken() {
  return localStorage.getItem("access");
}

export async function login(login_, password) {
  const response = await fetch(`${API_URL}/auth/token/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ login: login_, password }),
  });
  if (!response.ok) {
    throw new Error("Usuário ou senha inválidos");
  }
  const data = await response.json();
  localStorage.setItem("access", data.access);
  localStorage.setItem("refresh", data.refresh);
  return data;
}

export function logout() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
}

async function refreshAccessToken() {
  const refresh = localStorage.getItem("refresh");
  if (!refresh) {
    return false;
  }
  const response = await fetch(`${API_URL}/auth/token/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });
  if (!response.ok) {
    logout();
    return false;
  }
  const data = await response.json();
  localStorage.setItem("access", data.access);
  if (data.refresh) {
    localStorage.setItem("refresh", data.refresh);
  }
  return true;
}

function messageFromApiBody(body) {
  if (typeof body.detail === "string") {
    return body.detail;
  }
  if (Array.isArray(body.detail) && body.detail[0]) {
    return body.detail[0];
  }
  if (Array.isArray(body.non_field_errors) && body.non_field_errors[0]) {
    return body.non_field_errors[0];
  }
  const fieldError = Object.values(body).find(
    (value) => Array.isArray(value) && typeof value[0] === "string"
  );
  if (fieldError) {
    return fieldError[0];
  }
  return "Erro na API";
}

async function request(path, options = {}, retried = false) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (response.status === 401 && !retried) {
    const ok = await refreshAccessToken();
    if (ok) {
      return request(path, options, true);
    }
    throw new Error("Sessão expirada. Faça login de novo.");
  }
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(messageFromApiBody(error));
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
}

export const api = {
  guests: (params = "") => request(`/guests/${params}`),
  createGuest: (payload) =>
    request("/guests/", { method: "POST", body: JSON.stringify(payload) }),
  reservations: () => request("/reservations/"),
  createReservation: (payload) =>
    request("/reservations/", { method: "POST", body: JSON.stringify(payload) }),
  checkIn: (id) => request(`/reservations/${id}/check-in/`, { method: "POST" }),
  checkOut: (id) => request(`/reservations/${id}/check-out/`, { method: "POST" }),
};
