import { useState } from "react";

import { getToken } from "./api";
import { Home } from "./Home";
import { Login } from "./Login";

export function App() {
  const [loggedIn, setLoggedIn] = useState(Boolean(getToken()));

  if (!loggedIn) {
    return <Login onLoggedIn={() => setLoggedIn(true)} />;
  }
  return <Home onLogout={() => setLoggedIn(false)} />;
}
