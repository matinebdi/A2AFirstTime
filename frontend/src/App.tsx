import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { PageContextProvider } from './contexts/PageContext';
import { Layout } from './components/Layout';
import { Home } from './pages/Home';
import { Login } from './pages/Login';
import { SignUp } from './pages/SignUp';
import { Search } from './pages/Search';
import { Bookings } from './pages/Bookings';
import { Hotels } from './pages/Hotels';
import { HotelDetail } from './pages/HotelDetail';
import { PackageDetail } from './pages/PackageDetail';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <PageContextProvider>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Home />} />
              <Route path="search" element={<Search />} />
              <Route path="packages/:id" element={<PackageDetail />} />
              <Route path="hotels" element={<Hotels />} />
              <Route path="hotels/:locationId" element={<HotelDetail />} />
              <Route path="bookings" element={<Bookings />} />
              <Route path="login" element={<Login />} />
              <Route path="signup" element={<SignUp />} />
            </Route>
          </Routes>
        </PageContextProvider>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
