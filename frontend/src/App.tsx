import { useState } from "react";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import { UserContext } from "./contexts/userContext";
import type { User } from "./contexts/userContext";

function App() {
  const [user, setUser] = useState<User | null>(null);

  return (
    <UserContext.Provider value={{ user, setUser }}>
      <Login />
      <Profile />
    </UserContext.Provider>
  );
}

export default App;
