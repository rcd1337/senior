import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { api, logout } = vi.hoisted(() => ({
  logout: vi.fn(),
  api: {
    guests: vi.fn(),
    reservations: vi.fn(),
    createGuest: vi.fn(),
    createReservation: vi.fn(),
    checkIn: vi.fn(),
    checkOut: vi.fn(),
  },
}));

vi.mock("./api", () => ({ api, logout }));

import { Home } from "./Home";

const maria = {
  id: 1,
  name: "Maria Silva",
  document: "12345678900",
  phone: "11999990000",
};

describe("Home", () => {
  beforeEach(() => {
    api.guests.mockReset();
    api.reservations.mockReset();
    api.checkIn.mockReset();
    api.checkOut.mockReset();
    api.guests.mockResolvedValue([maria]);
    api.reservations.mockResolvedValue([]);
  });

  it("busca hóspede por nome, documento ou telefone", async () => {
    render(<Home onLogout={vi.fn()} />);
    await screen.findByRole("button", { name: "Buscar" });

    fireEvent.change(screen.getByPlaceholderText("Nome, documento ou telefone"), {
      target: { value: "Maria" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Buscar" }));

    await waitFor(() =>
      expect(api.guests).toHaveBeenCalledWith("?search=Maria")
    );
  });

  it("filtra hóspedes por status da reserva", async () => {
    render(<Home onLogout={vi.fn()} />);
    await screen.findByRole("button", { name: "Buscar" });

    const statusSelect = screen.getAllByRole("combobox")[0];
    fireEvent.change(statusSelect, { target: { value: "checked_in" } });
    fireEvent.click(screen.getByRole("button", { name: "Buscar" }));
    await waitFor(() =>
      expect(api.guests).toHaveBeenCalledWith("?status=checked_in")
    );

    fireEvent.change(statusSelect, { target: { value: "reserved" } });
    fireEvent.click(screen.getByRole("button", { name: "Buscar" }));
    await waitFor(() =>
      expect(api.guests).toHaveBeenCalledWith("?status=reserved")
    );

    fireEvent.change(statusSelect, { target: { value: "checked_out" } });
    fireEvent.click(screen.getByRole("button", { name: "Buscar" }));
    await waitFor(() =>
      expect(api.guests).toHaveBeenCalledWith("?status=checked_out")
    );
  });

  it("mostra alerta de check-in antes das 14h e o total no checkout", async () => {
    const reserved = {
      id: 10,
      status: "reserved",
      planned_check_in: "2026-08-26",
      planned_check_out: "2026-08-28",
      has_car: false,
      guest_detail: maria,
    };
    api.reservations.mockResolvedValue([reserved]);
    api.checkIn.mockImplementation(async () => {
      api.reservations.mockResolvedValue([{ ...reserved, status: "checked_in" }]);
      return {
        status: "checked_in",
        alert:
          "Check-in permitido a partir das 14h00. O procedimento foi registrado antes do horário previsto.",
      };
    });
    api.checkOut.mockResolvedValue({
      status: "checked_out",
      bill: {
        items: [
          {
            date: "2026-08-26",
            daily: "120.00",
            parking: "0.00",
            subtotal: "120.00",
          },
        ],
        late_checkout_fee: "60.00",
        total: "180.00",
      },
    });

    render(<Home onLogout={vi.fn()} />);
    fireEvent.click(await screen.findByRole("button", { name: "Check-in" }));
    expect(
      await screen.findByText(/Check-in permitido a partir das 14h00/)
    ).toBeInTheDocument();

    fireEvent.click(await screen.findByRole("button", { name: "Check-out" }));
    expect(await screen.findByText(/Total geral/)).toBeInTheDocument();
    expect(screen.getByText(/180,00/)).toBeInTheDocument();
  });
});
