import { useEffect, useState } from "react";

import { api, logout } from "./api";
import { CheckInAlert } from "./CheckInAlert";
import { CheckoutSummary } from "./CheckoutSummary";

const EMPTY_GUEST = { name: "", document: "", phone: "" };
const EMPTY_RESERVATION = {
  guest: "",
  planned_check_in: "",
  planned_check_out: "",
  has_car: false,
};

const STATUS_LABEL = {
  reserved: "Reservado",
  checked_in: "Hospedado",
  checked_out: "Check-out realizado",
};

export function Home({ onLogout }) {
  const [guests, setGuests] = useState([]);
  // Lista sem filtro — o <select> da reserva não pode seguir a busca da tela.
  const [allGuests, setAllGuests] = useState([]);
  const [reservations, setReservations] = useState([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [guestForm, setGuestForm] = useState(EMPTY_GUEST);
  const [reservationForm, setReservationForm] = useState(EMPTY_RESERVATION);
  const [alert, setAlert] = useState("");
  const [bill, setBill] = useState(null);
  const [error, setError] = useState("");

  async function loadGuests(nextSearch = search, nextStatus = statusFilter) {
    const params = new URLSearchParams();
    if (nextSearch) params.set("search", nextSearch);
    if (nextStatus) params.set("status", nextStatus);
    const query = params.toString() ? `?${params.toString()}` : "";
    setGuests(await api.guests(query));
  }

  async function loadAllGuests() {
    setAllGuests(await api.guests());
  }

  async function loadReservations() {
    setReservations(await api.reservations());
  }

  async function refresh() {
    setError("");
    await Promise.all([loadGuests(), loadAllGuests(), loadReservations()]);
  }

  useEffect(() => {
    refresh().catch((err) => setError(err.message));
  }, []);

  async function handleCreateGuest(event) {
    event.preventDefault();
    setError("");
    try {
      await api.createGuest(guestForm);
      setGuestForm(EMPTY_GUEST);
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleCreateReservation(event) {
    event.preventDefault();
    setError("");
    try {
      await api.createReservation({
        ...reservationForm,
        guest: Number(reservationForm.guest),
      });
      setReservationForm(EMPTY_RESERVATION);
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleCheckIn(id) {
    setError("");
    try {
      const data = await api.checkIn(id);
      setAlert(data.alert || "");
      setBill(null);
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleCheckOut(id) {
    setError("");
    try {
      const data = await api.checkOut(id);
      setAlert("");
      setBill(data.bill);
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main>
      <header className="top">
        <h1>Gestão de hóspedes</h1>
        <button
          type="button"
          onClick={() => {
            logout();
            onLogout();
          }}
        >
          Sair
        </button>
      </header>

      {error ? <p className="error">{error}</p> : null}
      <CheckInAlert message={alert} />

      <section className="card">
        <h2>Localizar hóspedes</h2>
        <div className="row">
          <input
            placeholder="Nome, documento ou telefone"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">Todos</option>
            <option value="checked_in">Hospedado</option>
            <option value="reserved">Reservado</option>
            <option value="checked_out">Check-out realizado</option>
          </select>
          <button type="button" onClick={() => loadGuests(search, statusFilter)}>
            Buscar
          </button>
        </div>
        <ul>
          {guests.map((guest) => (
            <li key={guest.id}>
              {guest.name} — {guest.document} — {guest.phone}
            </li>
          ))}
        </ul>
      </section>

      <section className="card">
        <h2>Novo hóspede</h2>
        <form onSubmit={handleCreateGuest} className="row">
          <input
            placeholder="Nome"
            value={guestForm.name}
            onChange={(e) => setGuestForm({ ...guestForm, name: e.target.value })}
            maxLength={150}
            required
          />
          <input
            placeholder="Documento"
            value={guestForm.document}
            onChange={(e) =>
              setGuestForm({ ...guestForm, document: e.target.value })
            }
            maxLength={30}
            required
          />
          <input
            placeholder="Telefone"
            value={guestForm.phone}
            onChange={(e) => setGuestForm({ ...guestForm, phone: e.target.value })}
            maxLength={30}
            required
          />
          <button type="submit">Cadastrar</button>
        </form>
      </section>

      <section className="card">
        <h2>Nova reserva</h2>
        <form onSubmit={handleCreateReservation} className="row">
          <select
            value={reservationForm.guest}
            onChange={(e) =>
              setReservationForm({ ...reservationForm, guest: e.target.value })
            }
            required
          >
            <option value="">Hóspede</option>
            {allGuests.map((guest) => (
              <option key={guest.id} value={guest.id}>
                {guest.name}
              </option>
            ))}
          </select>
          <input
            type="date"
            value={reservationForm.planned_check_in}
            onChange={(e) =>
              setReservationForm({
                ...reservationForm,
                planned_check_in: e.target.value,
              })
            }
            required
          />
          <input
            type="date"
            value={reservationForm.planned_check_out}
            onChange={(e) =>
              setReservationForm({
                ...reservationForm,
                planned_check_out: e.target.value,
              })
            }
            required
          />
          <label className="check">
            <input
              type="checkbox"
              checked={reservationForm.has_car}
              onChange={(e) =>
                setReservationForm({
                  ...reservationForm,
                  has_car: e.target.checked,
                })
              }
            />
            Precisa de vaga
          </label>
          <button type="submit">Reservar</button>
        </form>
      </section>

      <section className="card">
        <h2>Reservas</h2>
        <ul className="reservations">
          {reservations.map((item) => (
            <li key={item.id}>
              <div>
                <strong>{item.guest_detail.name}</strong> —{" "}
                {STATUS_LABEL[item.status] || item.status}
                <br />
                {item.planned_check_in} → {item.planned_check_out}
                {item.has_car ? " · com carro" : ""}
              </div>
              <div className="row">
                {item.status === "reserved" ? (
                  <button type="button" onClick={() => handleCheckIn(item.id)}>
                    Check-in
                  </button>
                ) : null}
                {item.status === "checked_in" ? (
                  <button type="button" onClick={() => handleCheckOut(item.id)}>
                    Check-out
                  </button>
                ) : null}
              </div>
            </li>
          ))}
        </ul>
      </section>

      <CheckoutSummary bill={bill} />
    </main>
  );
}
