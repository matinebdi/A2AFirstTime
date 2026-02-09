import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, Plane, Shield, Clock } from 'lucide-react';
import { packagesApi } from '../services/api';
import { PackageCard } from '../components/packages/PackageCard';
import { useSetPageContext } from '../contexts/PageContext';
import type { Package } from '../types';

export const Home: React.FC = () => {
  const [featuredPackages, setFeaturedPackages] = useState<Package[]>([]);
  const [loading, setLoading] = useState(true);
  const setPageContext = useSetPageContext();

  useEffect(() => {
    const fetchFeatured = async () => {
      try {
        const packages = await packagesApi.featured(6);
        setFeaturedPackages(packages);
      } catch (error) {
        console.error('Error fetching packages:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchFeatured();
  }, []);

  useEffect(() => {
    setPageContext({
      page: 'home',
      data: {
        featured_count: featuredPackages.length,
        featured_packages: featuredPackages.map((p) => ({ id: p.id, name: p.name })),
      },
    });
  }, [featuredPackages]);

  return (
    <div>
      {/* Hero Section */}
      <section className="relative h-[600px] bg-gradient-to-r from-blue-600 to-blue-800">
        <div
          className="absolute inset-0 bg-cover bg-center opacity-30"
          style={{
            backgroundImage:
              "url('https://images.unsplash.com/photo-1507525428034-b723cf961d3e')",
          }}
        />
        <div className="relative max-w-7xl mx-auto px-4 h-full flex flex-col justify-center">
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
            Vos vacances de reve
            <br />
            <span className="text-blue-200">en un clic</span>
          </h1>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl">
            Decouvrez nos packages tout compris avec l'aide de notre assistant IA.
            Transport, hebergement et activites inclus.
          </p>

          {/* Search Bar */}
          <div className="bg-white rounded-lg p-4 shadow-lg max-w-3xl">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-grow">
                <label className="text-sm text-gray-600 mb-1 block">
                  Destination
                </label>
                <input
                  type="text"
                  placeholder="Ou souhaitez-vous aller?"
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="text-sm text-gray-600 mb-1 block">
                  Budget max
                </label>
                <select className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option value="">Tous les budgets</option>
                  <option value="1000">Moins de 1000 Euros</option>
                  <option value="1500">Moins de 1500 Euros</option>
                  <option value="2000">Moins de 2000 Euros</option>
                  <option value="3000">Moins de 3000 Euros</option>
                </select>
              </div>
              <div className="flex items-end">
                <Link
                  to="/search"
                  className="w-full md:w-auto bg-blue-600 text-white px-8 py-2 rounded-lg hover:bg-blue-700 transition flex items-center justify-center"
                >
                  <Search className="h-5 w-5 mr-2" />
                  Rechercher
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Plane className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Tout Compris</h3>
              <p className="text-gray-600">
                Vol, hotel, activites et transfers inclus dans chaque package.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Paiement Securise</h3>
              <p className="text-gray-600">
                Transactions securisees via Stripe. Vos donnees sont protegees.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Clock className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Assistant 24/7</h3>
              <p className="text-gray-600">
                Notre assistant IA vous aide a trouver le voyage parfait.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Packages */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h2 className="text-3xl font-bold text-gray-900">
                Packages Populaires
              </h2>
              <p className="text-gray-600 mt-2">
                Nos destinations les plus appreciees
              </p>
            </div>
            <Link
              to="/search"
              className="text-blue-600 hover:underline font-medium"
            >
              Voir tous les packages
            </Link>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div
                  key={i}
                  className="bg-gray-200 rounded-xl h-80 animate-pulse"
                />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {featuredPackages.map((pkg) => (
                <PackageCard key={pkg.id} pkg={pkg} />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-blue-600">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Pret a partir en vacances?
          </h2>
          <p className="text-blue-100 mb-8 max-w-2xl mx-auto">
            Discutez avec notre assistant IA pour trouver le package ideal
            adapte a vos envies et votre budget.
          </p>
          <button
            onClick={() => {
              const chatButton = document.querySelector(
                'button[class*="fixed bottom-6 right-6"]'
              ) as HTMLButtonElement;
              chatButton?.click();
            }}
            className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition"
          >
            Discuter avec l'assistant
          </button>
        </div>
      </section>
    </div>
  );
};

export default Home;
