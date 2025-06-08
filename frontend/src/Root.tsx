import { Outlet } from "@tanstack/react-router"
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import { UserProvider } from "./contexts/userProvider";

export default function Root() {
  return (
    <UserProvider>
      <Outlet />
      <TanStackRouterDevtools />
    </UserProvider>
  )
}
