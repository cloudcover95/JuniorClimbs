# src/App.tsx
import React, { useState, useEffect } from 'react';

interface Product {
  id: number;
  sku: string;
  name: string;
  category: string;
  price_cents: number;
  stock: number;
}

interface CartItem {
  product_id: number;
  quantity: number;
  name?: string;
  price_cents?: number;
}

interface Transaction {
  id: string;
  total_cents: number;
  payment_method: string;
}

const API_BASE = 'http://localhost:8000';

export default function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'pos' | 'athletes'>('dashboard');
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [paymentMethod, setPaymentMethod] = useState<'cash' | 'card' | 'member' | 'crypto'>('cash');
  const [cryptoTxHash, setCryptoTxHash] = useState('');
  const [cryptoWallet, setCryptoWallet] = useState('');
  const [athletes, setAthletes] = useState<any[]>([]);
  const [newAthlete, setNewAthlete] = useState({ name: '', team: '', age: '' });
  const [lastTx, setLastTx] = useState<Transaction | null>(null);
  const [loading, setLoading] = useState(false);

  // Fetch products for POS
  const fetchProducts = async () => {
    try {
      const res = await fetch(`${API_BASE}/pos/products`);
      const data = await res.json();
      setProducts(data);
    } catch (e) {
      console.error('Failed to fetch products', e);
    }
  };

  // Fetch athletes
  const fetchAthletes = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/athletes`);
      const data = await res.json();
      setAthletes(data);
    } catch (e) {
      console.error('Failed to fetch athletes', e);
    }
  };

  useEffect(() => {
    if (activeTab === 'pos') fetchProducts();
    if (activeTab === 'athletes') fetchAthletes();
  }, [activeTab]);

  const addToCart = (product: Product) => {
    setCart(prev => {
      const existing = prev.findIndex(i => i.product_id === product.id);
      if (existing >= 0) {
        const updated = [...prev];
        updated[existing].quantity += 1;
        return updated;
      }
      return [...prev, { product_id: product.id, quantity: 1, name: product.name, price_cents: product.price_cents }];
    });
  };

  const removeFromCart = (index: number) => {
    setCart(prev => prev.filter((_, i) => i !== index));
  };

  const checkout = async () => {
    if (cart.length === 0) return;
    setLoading(true);
    try {
      const payload: any = {
        items: cart.map(i => ({ product_id: i.product_id, quantity: i.quantity })),
        payment_method: paymentMethod,
      };
      if (paymentMethod === 'crypto') {
        payload.crypto_tx_hash = cryptoTxHash || undefined;
        payload.crypto_wallet_address = cryptoWallet || undefined;
      }
      const res = await fetch(`${API_BASE}/pos/checkout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (res.ok) {
        setLastTx(data);
        setCart([]);
        setCryptoTxHash('');
        setCryptoWallet('');
        alert(`Checkout successful! TX: ${data.transaction_id}`);
        fetchProducts(); // refresh stock
      } else {
        alert(data.detail || 'Checkout failed');
      }
    } catch (e) {
      alert('Network error during checkout');
    } finally {
      setLoading(false);
    }
  };

  const createAthlete = async () => {
    if (!newAthlete.name) return;
    try {
      await fetch(`${API_BASE}/api/athletes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newAthlete.name,
          team: newAthlete.team || null,
          age: newAthlete.age ? parseInt(newAthlete.age) : null,
        }),
      });
      setNewAthlete({ name: '', team: '', age: '' });
      fetchAthletes();
    } catch (e) {
      alert('Failed to create athlete');
    }
  };

  const totalCents = cart.reduce((sum, item) => sum + (item.price_cents || 0) * item.quantity, 0);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-200">
      <div className="border-b border-zinc-800 bg-zinc-900">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-emerald-600 rounded flex items-center justify-center font-bold text-xl">JC</div>
            <div>
              <div className="font-semibold text-xl tracking-tight">JuniorClimbs</div>
              <div className="text-[10px] text-zinc-500 -mt-1">EDGE POS • v0.5.0</div>
            </div>
          </div>
          <div className="flex gap-1 bg-zinc-950 rounded-lg p-1 text-sm">
            {(['dashboard', 'pos', 'athletes'] as const).map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-5 py-1.5 rounded-md transition-all ${activeTab === tab ? 'bg-white text-zinc-950 font-medium' : 'hover:bg-zinc-900'}`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
          <div className="text-xs text-zinc-500">localhost:8000 • offline-first</div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* DASHBOARD */}
        {activeTab === 'dashboard' && (
          <div>
            <h1 className="text-4xl font-semibold tracking-tighter mb-2">Good afternoon, Coach.</h1>
            <p className="text-zinc-400 mb-8">Edge-native operations • Zero terminal • Crypto ready via Brave Wallet</p>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
                <div className="text-emerald-400 text-sm">TODAY'S REVENUE</div>
                <div className="text-5xl font-semibold tabular-nums mt-2">$1,284</div>
              </div>
              <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
                <div className="text-emerald-400 text-sm">ACTIVE ATHLETES</div>
                <div className="text-5xl font-semibold tabular-nums mt-2">{athletes.length || 42}</div>
              </div>
              <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
                <div className="text-emerald-400 text-sm">BITNET INFERENCE</div>
                <div className="text-5xl font-semibold tabular-nums mt-2">LIVE</div>
                <div className="text-xs text-zinc-500 mt-1">RFID + Camera telemetry active</div>
              </div>
            </div>
          </div>
        )}

        {/* POS */}
        {activeTab === 'pos' && (
          <div className="grid grid-cols-12 gap-6">
            <div className="col-span-7">
              <div className="flex justify-between items-end mb-4">
                <div>
                  <div className="text-3xl font-semibold tracking-tight">Point of Sale</div>
                  <div className="text-zinc-400">Day passes • Chalk • Shoes • Crypto via Brave</div>
                </div>
                <div className="text-right text-sm text-zinc-400">Stock synced • UUID ledger</div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {products.map(p => (
                  <div key={p.id} onClick={() => addToCart(p)} className="bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 rounded-2xl p-5 cursor-pointer transition-all active:scale-[0.985]">
                    <div className="font-medium">{p.name}</div>
                    <div className="text-xs text-zinc-400 mt-0.5">{p.sku} • {p.category}</div>
                    <div className="mt-4 flex justify-between items-baseline">
                      <div className="text-3xl font-semibold tabular-nums">${(p.price_cents / 100).toFixed(2)}</div>
                      <div className="text-emerald-400 text-sm">{p.stock} left</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="col-span-5 bg-zinc-900 border border-zinc-800 rounded-3xl p-6 flex flex-col">
              <div className="font-medium text-lg mb-4 flex justify-between">
                <span>Cart</span>
                <span className="text-emerald-400 tabular-nums">${(totalCents / 100).toFixed(2)}</span>
              </div>
              {cart.length === 0 && <div className="text-zinc-500 text-sm flex-1 flex items-center justify-center">Cart is empty. Tap products to add.</div>}
              {cart.length > 0 && (
                <div className="space-y-2 flex-1 overflow-auto pr-1">
                  {cart.map((item, idx) => (
                    <div key={idx} className="flex justify-between items-center bg-zinc-950 rounded-xl px-4 py-3 text-sm">
                      <div>{item.name} × {item.quantity}</div>
                      <button onClick={() => removeFromCart(idx)} className="text-red-400 hover:text-red-500">×</button>
                    </div>
                  ))}
                </div>
              )}

              <div className="mt-auto pt-6 border-t border-zinc-800 space-y-4">
                <div>
                  <div className="text-xs text-zinc-400 mb-1.5">PAYMENT METHOD</div>
                  <select value={paymentMethod} onChange={e => setPaymentMethod(e.target.value as any)} className="w-full bg-zinc-950 border border-zinc-700 rounded-xl px-4 py-3 text-sm">
                    <option value="cash">Cash</option>
                    <option value="card">Card</option>
                    <option value="member">Member Account</option>
                    <option value="crypto">Crypto (Brave Wallet)</option>
                  </select>
                </div>

                {paymentMethod === 'crypto' && (
                  <div className="space-y-3">
                    <input value={cryptoTxHash} onChange={e => setCryptoTxHash(e.target.value)} placeholder="Brave Wallet TX hash (optional)" className="w-full bg-zinc-950 border border-zinc-700 rounded-xl px-4 py-3 text-sm placeholder:text-zinc-500" />
                    <input value={cryptoWallet} onChange={e => setCryptoWallet(e.target.value)} placeholder="Wallet address" className="w-full bg-zinc-950 border border-zinc-700 rounded-xl px-4 py-3 text-sm placeholder:text-zinc-500" />
                  </div>
                )}

                <button onClick={checkout} disabled={cart.length === 0 || loading} className="w-full py-4 rounded-2xl bg-emerald-600 hover:bg-emerald-500 disabled:bg-zinc-700 font-medium text-lg tracking-tight transition-all active:scale-[0.985]">
                  {loading ? 'Processing…' : `Checkout • $${(totalCents / 100).toFixed(2)}`}
                </button>
                <div className="text-[10px] text-center text-zinc-500">Offline ledger • UUID primary key • Ready for upstream sync</div>
              </div>
            </div>
          </div>
        )}

        {/* ATHLETES */}
        {activeTab === 'athletes' && (
          <div>
            <div className="text-3xl font-semibold tracking-tight mb-6">Athletes</div>
            <div className="grid grid-cols-5 gap-6">
              <div className="col-span-3 bg-zinc-900 border border-zinc-800 rounded-3xl p-6">
                <div className="text-sm text-zinc-400 mb-3">ROSTER</div>
                <div className="space-y-px">
                  {athletes.length > 0 ? athletes.map((a, i) => (
                    <div key={i} className="flex justify-between py-3 px-4 bg-zinc-950 rounded-xl text-sm">
                      <div>{a.name}</div>
                      <div className="text-zinc-400">{a.team || '—'} • {a.age || '—'}</div>
                    </div>
                  )) : <div className="text-zinc-500 py-8 text-center">No athletes yet. Add one →</div>}
                </div>
              </div>
              <div className="col-span-2 bg-zinc-900 border border-zinc-800 rounded-3xl p-6">
                <div className="text-sm text-zinc-400 mb-3">ADD NEW ATHLETE</div>
                <div className="space-y-3">
                  <input value={newAthlete.name} onChange={e => setNewAthlete({ ...newAthlete, name: e.target.value })} placeholder="Full name" className="w-full bg-zinc-950 border border-zinc-700 rounded-xl px-4 py-3" />
                  <input value={newAthlete.team} onChange={e => setNewAthlete({ ...newAthlete, team: e.target.value })} placeholder="Team / Squad" className="w-full bg-zinc-950 border border-zinc-700 rounded-xl px-4 py-3" />
                  <input value={newAthlete.age} onChange={e => setNewAthlete({ ...newAthlete, age: e.target.value })} placeholder="Age" type="number" className="w-full bg-zinc-950 border border-zinc-700 rounded-xl px-4 py-3" />
                  <button onClick={createAthlete} className="w-full py-3.5 rounded-2xl bg-white text-zinc-950 font-medium">Create Athlete</button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {lastTx && (
        <div className="fixed bottom-6 right-6 bg-emerald-950 border border-emerald-900 text-emerald-400 px-5 py-3 rounded-2xl text-sm flex items-center gap-3">
          Last TX: {lastTx.id} • {lastTx.payment_method}
          <button onClick={() => setLastTx(null)} className="ml-2 text-emerald-400/60 hover:text-emerald-400">×</button>
        </div>
      )}
    </div>
  );
}