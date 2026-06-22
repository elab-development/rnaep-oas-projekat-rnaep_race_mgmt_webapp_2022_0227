import { createBrowserRouter } from "react-router-dom";
import { MainLayout } from "@/layouts/MainLayout";
import {
  RequireAuth,
  RequireOrganiser,
  RequireParticipant,
} from "@/components/auth/ProtectedRoute";
import { LandingPage } from "@/pages/LandingPage";
import { LoginPage } from "@/pages/LoginPage";
import { RegisterPage } from "@/pages/RegisterPage";
import { BrowseRacesPage } from "@/pages/BrowseRacesPage";
import { RaceDetailPage } from "@/pages/RaceDetailPage";
import { MyRegistrationsPage } from "@/pages/MyRegistrationsPage";
import {
  PaymentFailedPage,
} from "@/pages/PaymentReturnPages";
import { PaymentSuccessPage } from "@/pages/PaymentSuccessPage";
import { OrganiserDashboardPage } from "@/pages/OrganiserDashboardPage";
import { OrganiserRaceRegistrationsPage } from "@/pages/OrganiserRaceRegistrationsPage";
import { CreateRacePage } from "@/pages/CreateRacePage";
import { EditRacePage } from "@/pages/EditRacePage";
import { ProfilePage } from "@/pages/ProfilePage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { RedirectPreserveSearch } from "@/components/RedirectPreserveSearch";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      { index: true, element: <LandingPage /> },
      { path: "login", element: <LoginPage /> },
      { path: "register", element: <RegisterPage /> },
      { path: "payment-success", element: <PaymentSuccessPage /> },
      { path: "payment-failed", element: <PaymentFailedPage /> },
      { path: "payments/success", element: <RedirectPreserveSearch to="/payment-success" /> },
      { path: "payments/cancel", element: <RedirectPreserveSearch to="/payment-failed" /> },
      {
        element: <RequireAuth />,
        children: [
          { path: "races", element: <BrowseRacesPage /> },
          { path: "races/:id", element: <RaceDetailPage /> },
          { path: "profile", element: <ProfilePage /> },
          {
            element: <RequireParticipant />,
            children: [
              { path: "registrations", element: <MyRegistrationsPage /> },
            ],
          },
          {
            element: <RequireOrganiser />,
            children: [
              { path: "organiser", element: <OrganiserDashboardPage /> },
              { path: "organiser/races/new", element: <CreateRacePage /> },
              { path: "organiser/races/:id/edit", element: <EditRacePage /> },
              {
                path: "organiser/races/:id/registrations",
                element: <OrganiserRaceRegistrationsPage />,
              },
            ],
          },
        ],
      },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);
