import { useState } from "react";

import { login } from "./api";

export function Login({ onLoggedIn }) {
  const [login_, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      await login(login_, password);
      onLoggedIn();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main className="card">
      <h1>Hotel</h1>
      <p>Login do atendente</p>
      <form onSubmit={handleSubmit}>
        <label>
          Usuário ou e-mail
          <input
            type="text"
            value={login_}
            onChange={(e) => setLogin(e.target.value)}
            required
          />
        </label>
        <label>
          Senha
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        {error ? <p className="error">{error}</p> : null}
        <button type="submit">Entrar</button>
      </form>
    </main>
  );
}
