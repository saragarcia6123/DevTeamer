import { Outlet } from "@tanstack/react-router"
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import { UserProvider } from "./contexts/userProvider";
import Scaffold from "./Scaffold";

export default function Root() {
  return (
    <UserProvider>
      <Scaffold>
        <Outlet />
        <TanStackRouterDevtools />
      </Scaffold>
    </UserProvider>
  )
}
