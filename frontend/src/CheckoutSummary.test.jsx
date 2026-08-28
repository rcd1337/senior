import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { CheckoutSummary } from "./CheckoutSummary";
import { formatBRL, weekdayLabel } from "./money";

describe("formatBRL", () => {
  it("formata valores no padrão brasileiro", () => {
    expect(formatBRL("120.00")).toMatch(/R\$\s*120,00/);
  });
});

describe("weekdayLabel", () => {
  it("marca sábado como fim de semana", () => {
    expect(weekdayLabel("2026-08-29")).toBe("fim de semana");
  });

  it("marca quarta como dia útil", () => {
    expect(weekdayLabel("2026-08-26")).toBe("dia útil");
  });
});

describe("CheckoutSummary", () => {
  it("mostra o total geral e a taxa de checkout tardio", () => {
    const bill = {
      items: [
        {
          date: "2026-08-26",
          daily: "120.00",
          parking: "15.00",
          subtotal: "135.00",
        },
      ],
      late_checkout_fee: "60.00",
      total: "195.00",
    };
    render(<CheckoutSummary bill={bill} />);
    expect(screen.getByText(/Total geral/)).toBeInTheDocument();
    expect(screen.getByText(/Taxa de check-out tardio/)).toBeInTheDocument();
    expect(screen.getByText(/195,00/)).toBeInTheDocument();
    expect(screen.getByText(/Estacionamento/)).toBeInTheDocument();
    expect(screen.getByText(/15,00/)).toBeInTheDocument();
  });
});
