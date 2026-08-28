import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { login } = vi.hoisted(() => ({ login: vi.fn() }));

vi.mock("./api", () => ({ login }));

import { Login } from "./Login";

describe("Login", () => {
  beforeEach(() => {
    login.mockReset();
  });

  it("chama onLoggedIn quando o atendente entra", async () => {
    login.mockResolvedValue({ access: "a", refresh: "r" });
    const onLoggedIn = vi.fn();
    render(<Login onLoggedIn={onLoggedIn} />);

    fireEvent.change(screen.getByLabelText("Usuário ou e-mail"), {
      target: { value: "atendente" },
    });
    fireEvent.change(screen.getByLabelText("Senha"), {
      target: { value: "teste123" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Entrar" }));

    await waitFor(() => expect(onLoggedIn).toHaveBeenCalled());
    expect(login).toHaveBeenCalledWith("atendente", "teste123");
  });

  it("mostra erro se usuário ou senha forem inválidos", async () => {
    login.mockRejectedValue(new Error("Usuário ou senha inválidos"));
    render(<Login onLoggedIn={vi.fn()} />);

    fireEvent.change(screen.getByLabelText("Usuário ou e-mail"), {
      target: { value: "errado@hotel.com" },
    });
    fireEvent.change(screen.getByLabelText("Senha"), {
      target: { value: "y" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Entrar" }));

    expect(
      await screen.findByText("Usuário ou senha inválidos")
    ).toBeInTheDocument();
  });
});
