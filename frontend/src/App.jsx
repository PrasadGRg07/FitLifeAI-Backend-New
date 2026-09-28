import { BrowserRouter as Router, Route, Routes, useLocation } from "react-router-dom";
import ProductList from "./pages/ProductList";
import ProductDetails from "./pages/ProductDetails";
import Navbar from "./components/layout/Navbar";
import Footer from "./components/layout/Footer";
import CartPage from "./pages/CartPage";
import LandingPage from "./pages/LandingPage";
import FeaturesPage from "./pages/FeaturePage"; 
import FeatureDetailPage from "./pages/FeatureDetailPage"; 
import AboutUsPage from "./pages/AboutUsPage";
import PlansPage from "./pages/PlansPage";
import Dashboard from "./pages/Dashboard"; 
import SettingProfilePage from "./pages/SettingProfilePage";
import Login from "./pages/auth/Login";
import Signup from "./pages/auth/Signup";
import Activity from "./pages/Activity"; 
import Predict from "./pages/Predict";
import Workout from "./pages/WorkOut";
import Leaderboard from "./pages/Leaderboard";
import AdminLogin from "./admin/Adminlogin";
import AdminPanel from "./admin/Adminpanel";

function AppContent() {
  const location = useLocation();
  const hideNavbar = location.pathname === "/dashboard" || location.pathname === "/settingprofile" || location.pathname === "/login"
    || location.pathname === "/signup" || location.pathname === "/activity" || location.pathname === "/predict"
    || location.pathname === "/workout" || location.pathname === "/leaderboard"
    || location.pathname === "/admin/login" || location.pathname === "/admin"
    ; // Hide navbar on these routes

  return (
    <>
      {!hideNavbar && <Navbar />}
      <div className={`min-h-screen bg-gray-50 ${!hideNavbar && location.pathname !== "/" ? "pt-16" : ""}`}>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/features" element={<FeaturesPage />} />
          <Route path="/feature/:id" element={<FeatureDetailPage />} />
          <Route path="/products" element={<ProductList />} />
          <Route path="/product/:id" element={<ProductDetails />} />
          <Route path="/cart" element={<CartPage />} />
          <Route path="/aboutus" element={<AboutUsPage />} />
          <Route path="/plans" element={<PlansPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/settingprofile" element={<SettingProfilePage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/leaderboard" element={<Leaderboard />} /> {/* Add this line to include the Leaderboard page route */}
          <Route path="/workout" element={<Workout />} /> {/* Add this line to include the Workout page route */}
          <Route path="/activity" element={<Activity />} /> {/* Add this line to include the Activity page route */}
          <Route path="/predict" element={<Predict />} /> {/* Add this line to include the Predict page route */}
          {/* Admin Routes */}
          <Route path="/admin/login" element={<AdminLogin />} />
          <Route path="/admin" element={<AdminPanel />} />
        </Routes>
      </div>
      <Footer />
    </>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;