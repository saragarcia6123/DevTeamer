import { StrictMode } from 'react'
import ReactDOM from 'react-dom/client'
import {
  RouterProvider,
  createRootRoute,
  createRoute,
  createRouter,
} from '@tanstack/react-router'
import './styles.css'
import { z } from 'zod'
import reportWebVitals from './reportWebVitals.ts'

import Root from './Root.tsx'
import Home from './pages/Home.tsx'
import Profile from './pages/Profile.tsx'
import Login from './pages/login/Login.tsx'
import AuthorizeLogin from './pages/login/AuthorizeLogin.tsx'
import Register from './pages/register/Register.tsx'
import RegisterSuccess from './pages/register/RegisterSuccess.tsx'
import ConfirmLogin from './pages/login/ConfirmLogin.tsx'
import VerifyProfile from './pages/verify/VerifyProfile.tsx'
import { ROUTES } from './routes.ts'

export const optionalEmail = z.preprocess(
  (val) => {
    return typeof val === 'string' && z.string().email().safeParse(val).success
      ? val
      : undefined;
  },
  z.string().email().optional()
);

const rootRoute = createRootRoute({
  component: Root
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: ROUTES.home,
  component: Home,
});

const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: ROUTES.login,
  validateSearch: z.object({ email: optionalEmail }),
  component: Login,
});

const confirmLoginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: ROUTES.confirmLogin,
  validateSearch: z.object({ email: optionalEmail }),
  component: ConfirmLogin,
});

const authorizeLoginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: ROUTES.authorizeLogin,
  component: AuthorizeLogin,
});

const registerRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: ROUTES.register,
  validateSearch: z.object({ email: optionalEmail }),
  component: Register,
});

const registerSuccessRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: ROUTES.registerSuccess,
  validateSearch: z.object({ email: optionalEmail }),
  component: RegisterSuccess,
});

const verifyProfileRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: ROUTES.verifyProfile,
  component: VerifyProfile,
});

const profileRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: ROUTES.profile,
  component: Profile,
});

const routeTree = rootRoute.addChildren([
  indexRoute,
  loginRoute,
  confirmLoginRoute,
  authorizeLoginRoute,
  registerRoute,
  registerSuccessRoute,
  verifyProfileRoute,
  profileRoute,
])

const router = createRouter({
  routeTree,
  context: {},
  defaultPreload: 'intent',
  scrollRestoration: true,
  defaultStructuralSharing: true,
  defaultPreloadStaleTime: 0,
})

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}

const rootElement = document.getElementById('app')
if (rootElement && !rootElement.innerHTML) {
  const root = ReactDOM.createRoot(rootElement)

  root.render(
    <StrictMode>
      <RouterProvider router={router} />
    </StrictMode>,
  )
}

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals()
