import streamlit as st
import os

from langchain_core.messages import HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from operator import itemgetter

# Fetch OpenAI API Key from environment (Streamlit secrets in production)
openai_api_key = os.getenv("OPENAI_API_KEY")

# Safety check
if not openai_api_key:
    st.error("❌ OpenAI API key not found. Please set it in Streamlit Cloud > Secrets.")
    st.stop()

# Initialize LangChain OpenAI model (GPT-4 Turbo)
from langchain_openai import ChatOpenAI
lang_model = ChatOpenAI(model="gpt-4-1106-preview", api_key=openai_api_key)

# System prompt (cleaned, no code block inside)
system_prompt = """
You are Astra — an AI assistant developed by AeroChain to help explain our smart sourcing and factory digitization solutions with clarity, professionalism, and a touch of approachability.

Your role:
1. Guide new engineers, collaborators, or curious minds through AeroChain's vision of a transparent, efficient, and intelligent supply chain ecosystem.
2. Explain technical processes (like data integration, supplier tracking, and AI-enhanced decision-making) using clear, simple language.
3. Refer to the user by name when available to personalize responses.
4. Make the conversation interactive — ask brief, reflective questions to ensure engagement.
5. Emphasize how our solution builds trust, enhances efficiency, and reduces administrative friction in aerospace supply chains.
6. Explain the below course if asked by the user:
import React, { useState, useEffect } from "react";
import "./App.css";
import Web3 from "web3";
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// ABI for a simplified smart contract (you would replace this with your actual contract ABI)
const vendorRegistryABI = [
  {
    "inputs": [
      {
        "internalType": "string",
        "name": "_vendorName",
        "type": "string"
      },
      {
        "internalType": "string",
        "name": "_partId",
        "type": "string"
      },
      {
        "internalType": "string",
        "name": "_contactInfo",
        "type": "string"
      }
    ],
    "name": "registerVendor",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "getVendorCount",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  }
];

function App() {
  const [isLogin, setIsLogin] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [form, setForm] = useState({ email: "", password: "" });
  const [selectedPart, setSelectedPart] = useState(null);
  const [web3, setWeb3] = useState(null);
  const [account, setAccount] = useState(null);
  const [contract, setContract] = useState(null);
  const [vendorForm, setVendorForm] = useState({
    companyName: "",
    contactEmail: "",
    phoneNumber: "",
    supplierCapacity: "",
    certification: "",
    deliveryTime: ""
  });
  const [isBlockchainConnected, setIsBlockchainConnected] = useState(false);
  const [txStatus, setTxStatus] = useState("");
  
  // New state from App(1).js
  const [page, setPage] = useState("overview-dashboard");
  const [subPage, setSubPage] = useState(null);
  const [vendorControlOpen, setVendorControlOpen] = useState(false);
  const [showVendorForm, setShowVendorForm] = useState(false);

  // Sample vendors data
  const vendors = [
    { id: 1, name: "AeroTech Industries", rating: 4.8, location: "Seattle, WA", blockchain: true, activeContracts: 12, contactPerson: "John Smith", email: "jsmith@aerotech.com", phone: "206-555-1234", deliveryPerformance: 98, qualityScore: 95, avgLeadTime: 14 },
    { id: 2, name: "TitaniumPro Supplies", rating: 4.5, location: "Phoenix, AZ", blockchain: true, activeContracts: 8, contactPerson: "Sarah Johnson", email: "sjohnson@titanium.com", phone: "480-555-9876", deliveryPerformance: 92, qualityScore: 97, avgLeadTime: 18 },
    { id: 3, name: "Global Aero Components", rating: 4.2, location: "Dallas, TX", blockchain: true, activeContracts: 5, contactPerson: "David Williams", email: "dwilliams@globalaero.com", phone: "214-555-4321", deliveryPerformance: 89, qualityScore: 90, avgLeadTime: 21 },
    { id: 4, name: "Precision Aerospace", rating: 4.7, location: "Boston, MA", blockchain: false, activeContracts: 3, contactPerson: "Michelle Brown", email: "mbrown@precision.com", phone: "617-555-7890", deliveryPerformance: 94, qualityScore: 93, avgLeadTime: 16 },
  ];
  
  // Sample ongoing orders
  const ongoingOrders = [
    { id: 1, partName: "Turbofan Blade", companyName: "AeroTech Industries", count: 500, orderDate: "2025-03-15", deliveryDate: "2025-04-20", progress: 65, forecastDelivery: "On time", status: "In Production" },
    { id: 2, partName: "Actuator Arm", companyName: "TitaniumPro Supplies", count: 300, orderDate: "2025-03-10", deliveryDate: "2025-04-15", progress: 80, forecastDelivery: "Early (Apr 12)", status: "Final Testing" },
    { id: 3, partName: "Landing Gear Shaft", companyName: "Global Aero Components", count: 150, orderDate: "2025-03-20", deliveryDate: "2025-04-25", progress: 40, forecastDelivery: "Delayed (May 2)", status: "Production" },
    { id: 4, partName: "Avionics Heat Sink", companyName: "Precision Aerospace", count: 800, orderDate: "2025-03-01", deliveryDate: "2025-04-10", progress: 95, forecastDelivery: "On time", status: "Quality Control" },
  ];
  
  // Sample current inventory with cost data
  const currentInventory = [
    { id: 1, partName: "Turbofan Blade", companyName: "AeroTech Industries", count: 1250, lastUpdate: "2025-04-02", nextOrderDue: "2025-04-30", minThreshold: 1000, unitCost: 3200, reorderCost: 150000, leadTime: 14 },
    { id: 2, partName: "Actuator Arm", companyName: "TitaniumPro Supplies", count: 450, lastUpdate: "2025-04-03", nextOrderDue: "2025-04-15", minThreshold: 400, unitCost: 850, reorderCost: 42000, leadTime: 10 },
    { id: 3, partName: "Landing Gear Shaft", companyName: "Global Aero Components", count: 180, lastUpdate: "2025-04-01", nextOrderDue: "2025-04-10", minThreshold: 200, unitCost: 4500, reorderCost: 90000, leadTime: 21 },
    { id: 4, partName: "Avionics Heat Sink", companyName: "Precision Aerospace", count: 780, lastUpdate: "2025-04-05", nextOrderDue: "2025-05-15", minThreshold: 500, unitCost: 320, reorderCost: 25000, leadTime: 7 },
    { id: 5, partName: "Servo Bracket Assembly", companyName: "AeroTech Industries", count: 620, lastUpdate: "2025-04-04", nextOrderDue: "2025-04-20", minThreshold: 400, unitCost: 275, reorderCost: 18000, leadTime: 8 },
    { id: 6, partName: "Composite Fuselage Panel", companyName: "Global Aero Components", count: 320, lastUpdate: "2025-04-02", nextOrderDue: "2025-04-12", minThreshold: 300, unitCost: 5800, reorderCost: 175000, leadTime: 30 },
  ];
  
  // Sample vendor performance data for charts
  const vendorPerformanceData = [
    { month: 'Nov', onTime: 85, quality: 88, blockchain: 60 },
    { month: 'Dec', onTime: 87, quality: 89, blockchain: 65 },
    { month: 'Jan', onTime: 89, quality: 91, blockchain: 72 },
    { month: 'Feb', onTime: 91, quality: 93, blockchain: 78 },
    { month: 'Mar', onTime: 93, quality: 94, blockchain: 85 },
    { month: 'Apr', onTime: 92, quality: 95, blockchain: 90 },
  ];
  
  // Sample blockchain activity data
  const blockchainActivityData = [
    { month: 'Nov', contracts: 8, verifications: 12 },
    { month: 'Dec', contracts: 15, verifications: 18 },
    { month: 'Jan', contracts: 22, verifications: 25 },
    { month: 'Feb', contracts: 28, verifications: 32 },
    { month: 'Mar', contracts: 35, verifications: 40 },
    { month: 'Apr', contracts: 42, verifications: 45 },
  ];
  
  // Sample inventory data
  const inventoryLevelsData = [
    { name: 'Turbofan Blade', value: 1250, threshold: 1000 },
    { name: 'Actuator Arm', value: 450, threshold: 400 },
    { name: 'Landing Gear Shaft', value: 180, threshold: 200 },
    { name: 'Avionics Heat Sink', value: 780, threshold: 500 },
    { name: 'Servo Bracket', value: 620, threshold: 400 },
    { name: 'Fuselage Panel', value: 320, threshold: 300 },
  ];
  
  // Sample lead time data
  const leadTimeData = [
    { vendor: 'AeroTech', quoted: 14, actual: 15 },
    { vendor: 'TitaniumPro', quoted: 18, actual: 17 },
    { vendor: 'Global Aero', quoted: 21, actual: 23 },
    { vendor: 'Precision', quoted: 16, actual: 16 },
  ];
  
  // Sample supplier distribution data
  const supplierDistributionData = [
    { name: 'West Coast', value: 35 },
    { name: 'Midwest', value: 20 },
    { name: 'East Coast', value: 25 },
    { name: 'South', value: 15 },
    { name: 'International', value: 5 },
  ];

  const parts = [
    {
      id: 1,
      name: "Turbofan Blade",
      material: "Titanium Alloy",
      lastUpdated: "3 days ago",
      status: "Public",
      specs: {
        Design: "Aerodynamic profile optimized for low drag",
        Quantitative: "Weight - 2.5 kg/m²",
        "Type of Material": "Carbon Fiber Reinforced Polymer",
        "Thermal Conductivity": "0.2 W/m·K",
        "Tensile Strength": "600 MPa",
        "Elastic Modulus": "70 GPa",
        "Fatigue Limit": "200 MPa",
        "Corrosion Resistance": "Excellent in harsh environments",
        "Operating Temperature": "-50°C to 120°C",
        Color: "Black with a glossy finish",
        Applications: "Aerospace components, UAVs, automotive parts",
        Certifications: "ISO 9001, AS9100",
        "Manufacturing Process": "Automated Fiber Placement (AFP)",
        "Surface Treatment": "UV-resistant coating",
        Availability: "In stock, ready for immediate shipment",
        "Lead Time": "2 weeks for bulk orders",
      },
    },
    {
      id: 2,
      name: "Actuator Arm",
      material: "Aluminum 7075",
      lastUpdated: "1 day ago",
      status: "Private",
      specs: {
        Design: "Optimized for actuation",
        Quantitative: "Weight - 1.8 kg/m²",
        "Type of Material": "Aluminum 7075",
        "Tensile Strength": "500 MPa",
        "Elastic Modulus": "71 GPa",
        Availability: "Made to order",
        "Lead Time": "3 weeks",
        Applications: "Control surfaces, landing systems",
      },
    },
    {
      id: 3,
      name: "Landing Gear Shaft",
      material: "Steel 4340",
      lastUpdated: "4 days ago",
      status: "Public",
      specs: {
        Design: "Cylindrical shaft with high load tolerance",
        "Tensile Strength": "1080 MPa",
        Weight: "5.2 kg",
        Finish: "Zinc-plated",
        Applications: "Retractable landing gear",
        Certifications: "ISO 14001",
        "Lead Time": "2 weeks",
      },
    },
    {
      id: 4,
      name: "Avionics Heat Sink",
      material: "Copper-Tungsten",
      lastUpdated: "2 days ago",
      status: "Private",
      specs: {
        Design: "Modular fin-based heatsink",
        "Thermal Conductivity": "200 W/m·K",
        Finish: "Anodized Black",
        Applications: "Radar and avionics modules",
        Certifications: "RoHS, MIL-STD-810",
        Availability: "In stock",
        "Lead Time": "1 week",
      },
    },
    {
      id: 5,
      name: "Servo Bracket Assembly",
      material: "Stainless Steel 316L",
      lastUpdated: "6 days ago",
      status: "Public",
      specs: {
        Design: "Reinforced L-shaped bracket with multi-axis mount",
        Quantitative: "Weight - 0.95 kg",
        "Type of Material": "316L Stainless Steel",
        "Tensile Strength": "580 MPa",
        "Elastic Modulus": "193 GPa",
        Corrosion: "Excellent marine-grade resistance",
        Compatibility: "Standard aerospace servos (JR, Futaba)",
        Applications: "Control linkages in UAVs, stabilizers",
        Certifications: "NADCAP Compliant",
        Finish: "Electropolished",
        Availability: "Custom and standard sizes in stock",
        "Lead Time": "5–7 business days",
      }
    },
    {
      id: 6,
      name: "Composite Fuselage Panel",
      material: "Carbon Fiber Composite",
      lastUpdated: "Today",
      status: "Public",
      specs: {
        Design: "Honeycomb core sandwich panel for lightweight strength",
        Quantitative: "Weight - 3.0 kg/m²",
        "Type of Material": "Epoxy resin with carbon fiber",
        "Thermal Conductivity": "0.15 W/m·K",
        "Tensile Strength": "900 MPa",
        "Elastic Modulus": "85 GPa",
        "Impact Resistance": "High energy absorption",
        FireResistance: "Meets FAR 25.853",
        Applications: "Fuselage skin, fairings, access panels",
        Certifications: "FAA Certified, ISO 9001",
        "Manufacturing Process": "Autoclave cured",
        "Surface Treatment": "Fire-retardant coating",
        Availability: "Limited stock",
        "Lead Time": "3–4 weeks",
      }
    },
    {
      id: 7,
      name: "Flight Control Linkage",
      material: "Titanium Grade 5",
      lastUpdated: "Yesterday",
      status: "Private",
      specs: {
        Design: "Precision-machined rod with clevis ends",
        Quantitative: "Weight - 0.6 kg",
        "Tensile Strength": "950 MPa",
        "Elastic Modulus": "114 GPa",
        Corrosion: "High resistance in salt spray environment",
        Compatibility: "Universal aerospace actuator interfaces",
        Applications: "Elevator and aileron actuation systems",
        Finish: "Passivated surface",
        Certifications: "AMS 4911 Compliant",
        Availability: "Available upon request",
        "Lead Time": "2–3 weeks",
      }
    },
    {
      id: 8,
      name: "High-Precision Gearbox",
      material: "Nitrided Alloy Steel",
      lastUpdated: "5 days ago",
      status: "Public",
      specs: {
        Design: "Compact planetary gear system with high torque output",
        Quantitative: "Torque - 300 Nm, Weight - 2.3 kg",
        "Gear Ratio": "50:1",
        Lubrication: "Synthetic aerospace-grade grease",
        Applications: "Robotic joints, actuator drives",
        Certifications: "AS9100, ISO 9001",
        Compatibility: "Brushless DC and stepper motors",
        Finish: "Nickel-coated housing",
        Availability: "In stock for limited runs",
        "Lead Time": "7–10 business days",
      }
    },    
  ];
  
  // New data structures from App(1).js
  const orders = [
    { id: "#001", item: "Servo Bracket", qty: 100, status: "Shipped" },
    { id: "#002", item: "Heat Sink", qty: 50, status: "Pending" },
  ];

  const completedOrders = [
    { id: "#12345", rating: 5, comments: "Great service!" },
  ];
  
  // State for selected vendor or part details
  const [selectedVendor, setSelectedVendor] = useState(null);
  const [selectedInventoryPart, setSelectedInventoryPart] = useState(null);
  
  // Initialize Web3 connection
  useEffect(() => {
    const initWeb3 = async () => {
      if (window.ethereum) {
        try {
          // Request account access
          await window.ethereum.request({ method: 'eth_requestAccounts' });
          const web3Instance = new Web3(window.ethereum);
          setWeb3(web3Instance);
          
          // Get connected account
          const accounts = await web3Instance.eth.getAccounts();
          setAccount(accounts[0]);
          
          // Connect to smart contract (replace with your contract address)
          const contractAddress = "0x1234567890123456789012345678901234567890"; // Example address
          const contractInstance = new web3Instance.eth.Contract(
            vendorRegistryABI,
            contractAddress
          );
          setContract(contractInstance);
          setIsBlockchainConnected(true);
        } catch (error) {
          console.error("User denied account access or error occurred:", error);
        }
      } else {
        console.log("Please install MetaMask or another Ethereum wallet provider.");
      }
    };
    
    initWeb3();
  }, []);

  const handleLogin = () => {
    if (form.email && form.password) {
      setIsLoggedIn(true);
    } else {
      alert("Please enter both email and password.");
    }
  };
  
  const handleVendorFormChange = (e) => {
    setVendorForm({
      ...vendorForm,
      [e.target.name]: e.target.value
    });
  };
  
  const handleVendorSubmit = async () => {
    if (!isBlockchainConnected) {
      alert("Please connect to blockchain first");
      return;
    }
    
    setTxStatus("Submitting to blockchain...");
    
    try {
      // Call the smart contract function
      await contract.methods.registerVendor(
        vendorForm.companyName,
        selectedPart.id.toString(),
        JSON.stringify({
          email: vendorForm.contactEmail,
          phone: vendorForm.phoneNumber,
          capacity: vendorForm.supplierCapacity,
          certification: vendorForm.certification,
          deliveryTime: vendorForm.deliveryTime
        })
      ).send({ from: account });
      
      setTxStatus("Successfully registered on blockchain!");
      setTimeout(() => {
        setSelectedPart(null);
        setTxStatus("");
      }, 3000);
    } catch (error) {
      console.error("Transaction failed:", error);
      setTxStatus("Transaction failed. See console for details.");
    }
  };

  if (!isLoggedIn) {
    return (
      <div className="auth-container">
        <div className="auth-left">
          <h1>Welcome to Areochain: Blockchain-Powered Procurement Platform</h1>
        </div>

        <div className="auth-right">
          <div className="auth-card">
            <div className="auth-tabs">
              <button
                className={isLogin ? "active" : ""}
                onClick={() => setIsLogin(true)}
              >
                Login
              </button>
              <button
                className={!isLogin ? "active" : ""}
                onClick={() => setIsLogin(false)}
              >
                Sign Up
              </button>
            </div>

            {isLogin ? (
              <>
                <input
                  type="email"
                  placeholder="Email"
                  onChange={(e) =>
                    setForm({ ...form, email: e.target.value })
                  }
                />
                <input
                  type="password"
                  placeholder="Password"
                  onChange={(e) =>
                    setForm({ ...form, password: e.target.value })
                  }
                />
                <div className="forgot">Forgot password?</div>
                <button className="primary" onClick={handleLogin}>
                  Login
                </button>
                <button className="secondary">Continue with Google</button>
              </>
            ) : (
              <>
                <input type="text" placeholder="Full Name" />
                <input type="email" placeholder="Email" />
                <input type="tel" placeholder="Phone Number" />
                <input type="password" placeholder="Password" />
                <button className="primary" onClick={handleLogin}>
                  Register
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="sidebar">
        <h2>{page === "vendors" ? "Performance Dashboard" : "Dashboard"}</h2>
        <ul>
          <li onClick={() => setPage("overview-dashboard")}>📊 Analytics Dashboard</li>
          <li onClick={() => setPage("dashboard")}>👥 Buyers</li>
          <li onClick={() => setPage("orders")}>📦 Orders</li>
          <li onClick={() => setPage("vendors")}>🏭 Vendors</li>
          <li onClick={() => setVendorControlOpen(!vendorControlOpen)}>
            🛠 Vendor Control {vendorControlOpen ? "▾" : "▸"}
          </li>
          {vendorControlOpen && (
            <ul className="sub-menu">
              <li onClick={() => { setPage("vendor-control"); setSubPage("bids"); }}>📩 Bids</li>
              <li onClick={() => { setPage("vendor-control"); setSubPage("followups"); }}>⏰ Follow Ups</li>
              <li onClick={() => { setPage("vendor-control"); setSubPage("trusted"); }}>⭐ Trusted Sources</li>
            </ul>
          )}
          <li>⛓️ Blockchain Status: {isBlockchainConnected ? 
              <span className="status-connected">Connected</span> : 
              <span className="status-disconnected">Disconnected</span>}
          </li>
          {account && <li className="account-info">🔑 {account.substring(0, 6)}...{account.substring(account.length - 4)}</li>}
        </ul>
      </div>

      <div className="main-content">
      {page === "overview-dashboard" && (
  <div className="dashboard-overview">
    <h2>Aerospace Procurement Analytics</h2>
    
    {/* Top KPIs row */}
    <div className="kpi-row">
      <div className="kpi-card">
        <h3>Verified Vendors</h3>
        <div className="kpi-value">24 <span className="blockchain-verified">⛓️</span></div>
      </div>
      <div className="kpi-card">
        <h3>On-time Delivery</h3>
        <div className="kpi-value">92%</div>
      </div>
      <div className="kpi-card">
        <h3>Active Contracts</h3>
        <div className="kpi-value">37</div>
      </div>
      <div className="kpi-card">
        <h3>Inventory Value</h3>
        <div className="kpi-value">$7.4M</div>
        <div className="kpi-subtitle">Avg. Reorder Cost: $83.3K</div>
      </div>
    </div>
    
    {/* MOVED: Supplier Distribution and Inventory Levels first */}
    <div className="section-header">
      <h3>Inventory & Supplier Overview</h3>
    </div>
    <div className="charts-grid">
      <div className="chart-container">
        <h3>Supplier Distribution</h3>
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={supplierDistributionData}
              cx="50%"
              cy="50%"
              labelLine={true}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
              nameKey="name"
              label={({name, percent}) => `${name}: ${(percent * 100).toFixed(0)}%`}
            >
              {supplierDistributionData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'][index % 5]} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => `${value}%`} />
          </PieChart>
        </ResponsiveContainer>
      </div>
      
      <div className="chart-container">
        <h3>Inventory Levels</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={inventoryLevelsData} layout="vertical" margin={{ top: 5, right: 30, left: 50, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey="name" type="category" />
            <Tooltip />
            <Legend />
            <Bar dataKey="value" fill="#82ca9d" name="Current Stock">
              {inventoryLevelsData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.value < entry.threshold ? '#ff8042' : '#82ca9d'} />
              ))}
            </Bar>
            <Bar dataKey="threshold" fill="#8884d8" name="Min Threshold" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
    
    {/* MOVED: Current Inventory Status Section next */}
    <div className="section-header">
      <h3>Current Inventory Status</h3>
    </div>
    <div className="data-table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th>Part Name</th>
            <th>Supplier</th>
            <th>Current Count</th>
            <th>Last Updated</th>
            <th>Next Order Due</th>
            <th>Inventory Status</th>
          </tr>
        </thead>
        <tbody>
          {currentInventory.map(item => (
            <tr key={item.id}>
              <td><a href="#" onClick={(e) => {e.preventDefault(); setSelectedInventoryPart(parts.find(p => p.name === item.partName));}}>{item.partName}</a></td>
              <td><a href="#" onClick={(e) => {e.preventDefault(); setSelectedVendor(vendors.find(v => v.name === item.companyName));}}>{item.companyName}</a></td>
              <td>{item.count.toLocaleString()}</td>
              <td>{new Date(item.lastUpdate).toLocaleDateString()}</td>
              <td>{new Date(item.nextOrderDue).toLocaleDateString()}</td>
              <td className={item.count < item.minThreshold ? "low-inventory" : "good-inventory"}>
                {item.count < item.minThreshold ? "Low Stock" : "Good"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
    
    {/* Order Tracking Section */}
    <div className="section-header">
      <h3>Ongoing Orders</h3>
    </div>
    <div className="data-table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th>Part Name</th>
            <th>Vendor</th>
            <th>Quantity</th>
            <th>Delivery Date</th>
            <th>Progress</th>
            <th>Delivery Forecast</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {ongoingOrders.map(order => (
            <tr key={order.id}>
              <td><a href="#" onClick={(e) => {e.preventDefault(); setSelectedInventoryPart(parts.find(p => p.name === order.partName));}}>{order.partName}</a></td>
              <td><a href="#" onClick={(e) => {e.preventDefault(); setSelectedVendor(vendors.find(v => v.name === order.companyName));}}>{order.companyName}</a></td>
              <td>{order.count.toLocaleString()}</td>
              <td>{new Date(order.deliveryDate).toLocaleDateString()}</td>
              <td>
                <div className="progress-bar-container">
                  <div className="progress-bar" style={{width: `${order.progress}%`}}></div>
                  <span className="progress-text">{order.progress}%</span>
                </div>
              </td>
              <td className={order.forecastDelivery.includes("Delayed") ? "delayed" : order.forecastDelivery.includes("Early") ? "early" : "on-time"}>
                {order.forecastDelivery}
              </td>
              <td>{order.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>

    {/* Charts section - remaining charts */}
    <div className="section-header">
      <h3>Performance Analytics</h3>
    </div>
    <div className="charts-grid">
      <div className="chart-container large">
        <h3>Vendor Performance Timeline</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={vendorPerformanceData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="onTime" stroke="#8884d8" name="On-time Delivery %" />
            <Line type="monotone" dataKey="quality" stroke="#82ca9d" name="Quality Score" />
            <Line type="monotone" dataKey="blockchain" stroke="#ffc658" name="Blockchain Verified %" />
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      <div className="chart-container">
        <h3>Blockchain Contract Activity</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={blockchainActivityData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="contracts" fill="#8884d8" name="New Contracts" />
            <Bar dataKey="verifications" fill="#82ca9d" name="Verifications" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      <div className="chart-container">
        <h3>Lead Time Analysis</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={leadTimeData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="vendor" />
            <YAxis label={{ value: 'Days', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Bar dataKey="quoted" fill="#8884d8" name="Quoted Lead Time" />
            <Bar dataKey="actual" fill="#82ca9d" name="Actual Lead Time" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
    
    <div className="blockchain-status-panel">
      <h3>⛓️ Blockchain Network Status</h3>
      <div className="status-grid">
        <div className="status-item">
          <span className="status-label">Network:</span>
          <span className="status-value">Ethereum Mainnet</span>
        </div>
        <div className="status-item">
          <span className="status-label">Connected Account:</span>
          <span className="status-value">{account ? `${account.substring(0, 6)}...${account.substring(account.length - 4)}` : "Not connected"}</span>
        </div>
        <div className="status-item">
          <span className="status-label">Smart Contract:</span>
          <span className="status-value">VendorRegistry</span>
        </div>
        <div className="status-item">
          <span className="status-label">Connection Status:</span>
          <span className="status-value">{isBlockchainConnected ? "Connected ✅" : "Disconnected ❌"}</span>
        </div>
      </div>
    </div>
  </div>
)}
        
        {page === "dashboard" && (
          <>
            <div className="header-banner">
              <h2>Aerospace Part Catalog</h2>
              <div className="blockchain-indicator">
                {isBlockchainConnected ? 
                  <span className="blockchain-connected">⛓️ Blockchain Connected</span> : 
                  <span className="blockchain-disconnected">⛓️ Connect Wallet</span>}
              </div>
            </div>
            
            {parts.map((part) => (
              <div className="buyer-card" key={part.id}>
                <h3>{part.name}</h3>
                <p>
                  <strong>Material:</strong> {part.material}
                </p>
                <p>
                  <strong>Last Updated:</strong> {part.lastUpdated}
                </p>
                <p>
                  <strong>Status:</strong> {part.status}
                </p>
                <button onClick={() => setSelectedPart(part)}>More Info</button>
              </div>
            ))}
          </>
        )}

{page === "orders" && (
  <>
    <div className="header-banner">
      <h2>Inventory & Order Management</h2>
      <div className="blockchain-indicator">
        {isBlockchainConnected ? 
          <span className="blockchain-connected">⛓️ Blockchain Verification Active</span> : 
          <span className="blockchain-disconnected">⛓️ Connect Wallet for Verification</span>}
      </div>
    </div>

    {/* File Upload Section */}
    <div className="section-header">
      <h3>Upload Inventory Data</h3>
    </div>
    <div className="upload-box">
      <div style={{ marginBottom: "15px" }}>
        <i className="fa fa-upload" style={{ fontSize: "32px", color: "#e53935", marginBottom: "10px" }}></i>
        <p>Drag and drop inventory files here or click to browse</p>
        <p style={{ fontSize: "12px", color: "#666" }}>Supported formats: XLS, XLSX, CSV</p>
      </div>
      <button className="secondary">Select Files</button>
    </div>

    {/* Current Orders Section */}
    <div className="section-header">
      <h3>Current Orders</h3>
    </div>
    <div className="data-table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th>Order ID</th>
            <th>Part Name</th>
            <th>Vendor</th>
            <th>Quantity</th>
            <th>Order Date</th>
            <th>Expected Delivery</th>
            <th>Status</th>
            <th>Blockchain Verified</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>#ORD-2025-1042</td>
            <td>Turbofan Blade</td>
            <td>AeroTech Industries</td>
            <td>500</td>
            <td>Apr 1, 2025</td>
            <td>Apr 20, 2025</td>
            <td><span className="status-badge in-progress">In Production</span></td>
            <td><span className="blockchain-verified">✓</span></td>
            <td><button className="secondary small">View Details</button></td>
          </tr>
          <tr>
            <td>#ORD-2025-1039</td>
            <td>Actuator Arm</td>
            <td>TitaniumPro Supplies</td>
            <td>300</td>
            <td>Mar 28, 2025</td>
            <td>Apr 15, 2025</td>
            <td><span className="status-badge testing">Final Testing</span></td>
            <td><span className="blockchain-verified">✓</span></td>
            <td><button className="secondary small">View Details</button></td>
          </tr>
          <tr>
            <td>#ORD-2025-1035</td>
            <td>Landing Gear Shaft</td>
            <td>Global Aero Components</td>
            <td>150</td>
            <td>Mar 25, 2025</td>
            <td>Apr 25, 2025</td>
            <td><span className="status-badge delayed">Delayed</span></td>
            <td><span className="blockchain-verified">✓</span></td>
            <td><button className="secondary small">View Details</button></td>
          </tr>
          <tr>
            <td>#ORD-2025-1030</td>
            <td>Avionics Heat Sink</td>
            <td>Precision Aerospace</td>
            <td>800</td>
            <td>Mar 20, 2025</td>
            <td>Apr 10, 2025</td>
            <td><span className="status-badge qc">Quality Control</span></td>
            <td><span className="blockchain-pending">Pending</span></td>
            <td><button className="secondary small">View Details</button></td>
          </tr>
          <tr>
            <td>#ORD-2025-1028</td>
            <td>Servo Bracket Assembly</td>
            <td>AeroTech Industries</td>
            <td>250</td>
            <td>Mar 18, 2025</td>
            <td>Apr 12, 2025</td>
            <td><span className="status-badge shipped">Shipped</span></td>
            <td><span className="blockchain-verified">✓</span></td>
            <td><button className="secondary small">View Details</button></td>
          </tr>
        </tbody>
      </table>
    </div>

    {/* Inventory Management Section */}
    <div className="section-header">
      <h3>Inventory Management</h3>
    </div>
    <div className="inventory-controls" style={{ marginBottom: "20px", display: "flex", gap: "15px", alignItems: "center" }}>
      <input type="text" placeholder="Search parts..." style={{ flex: "1" }} />
      <select className="filter-dropdown" style={{ padding: "8px", borderRadius: "5px", border: "1px solid #ccc" }}>
        <option>All Locations</option>
        <option>Warehouse A</option>
        <option>Warehouse B</option>
        <option>Production Floor</option>
      </select>
      <select className="filter-dropdown" style={{ padding: "8px", borderRadius: "5px", border: "1px solid #ccc" }}>
        <option>All Status</option>
        <option>In Stock</option>
        <option>Low Stock</option>
        <option>Out of Stock</option>
      </select>
      <button className="primary">Filter</button>
    </div>

    <div className="data-table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th>Part ID</th>
            <th>Part Name</th>
            <th>Current Quantity</th>
            <th>Min Threshold</th>
            <th>Location</th>
            <th>Last Updated</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>P-1001</td>
            <td>Turbofan Blade</td>
            <td>1,250</td>
            <td>1,000</td>
            <td>Warehouse A</td>
            <td>Apr 5, 2025</td>
            <td><span className="inventory-status good">In Stock</span></td>
            <td>
              <div style={{ display: "flex", gap: "5px" }}>
                <button className="secondary small">Edit</button>
                <button className="primary small">Order</button>
              </div>
            </td>
          </tr>
          <tr>
            <td>P-1002</td>
            <td>Actuator Arm</td>
            <td>450</td>
            <td>400</td>
            <td>Warehouse A</td>
            <td>Apr 4, 2025</td>
            <td><span className="inventory-status warning">Low Stock</span></td>
            <td>
              <div style={{ display: "flex", gap: "5px" }}>
                <button className="secondary small">Edit</button>
                <button className="primary small">Order</button>
              </div>
            </td>
          </tr>
          <tr>
            <td>P-1003</td>
            <td>Landing Gear Shaft</td>
            <td>180</td>
            <td>200</td>
            <td>Warehouse B</td>
            <td>Apr 3, 2025</td>
            <td><span className="inventory-status critical">Below Threshold</span></td>
            <td>
              <div style={{ display: "flex", gap: "5px" }}>
                <button className="secondary small">Edit</button>
                <button className="primary small">Order</button>
              </div>
            </td>
          </tr>
          <tr>
            <td>P-1004</td>
            <td>Avionics Heat Sink</td>
            <td>780</td>
            <td>500</td>
            <td>Warehouse A</td>
            <td>Apr 6, 2025</td>
            <td><span className="inventory-status good">In Stock</span></td>
            <td>
              <div style={{ display: "flex", gap: "5px" }}>
                <button className="secondary small">Edit</button>
                <button className="primary small">Order</button>
              </div>
            </td>
          </tr>
          <tr>
            <td>P-1005</td>
            <td>Servo Bracket Assembly</td>
            <td>620</td>
            <td>400</td>
            <td>Production Floor</td>
            <td>Apr 5, 2025</td>
            <td><span className="inventory-status good">In Stock</span></td>
            <td>
              <div style={{ display: "flex", gap: "5px" }}>
                <button className="secondary small">Edit</button>
                <button className="primary small">Order</button>
              </div>
            </td>
          </tr>
          <tr>
            <td>P-1006</td>
            <td>Composite Fuselage Panel</td>
            <td>320</td>
            <td>300</td>
            <td>Warehouse B</td>
            <td>Apr 4, 2025</td>
            <td><span className="inventory-status warning">Low Stock</span></td>
            <td>
              <div style={{ display: "flex", gap: "5px" }}>
                <button className="secondary small">Edit</button>
                <button className="primary small">Order</button>
              </div>
            </td>
          </tr>
          <tr>
            <td>P-1007</td>
            <td>Flight Control Linkage</td>
            <td>500</td>
            <td>350</td>
            <td>Warehouse A</td>
            <td>Apr 2, 2025</td>
            <td><span className="inventory-status good">In Stock</span></td>
            <td>
              <div style={{ display: "flex", gap: "5px" }}>
                <button className="secondary small">Edit</button>
                <button className="primary small">Order</button>
              </div>
            </td>
          </tr>
          <tr>
            <td>P-1008</td>
            <td>High-Precision Gearbox</td>
            <td>75</td>
            <td>100</td>
            <td>Production Floor</td>
            <td>Apr 6, 2025</td>
            <td><span className="inventory-status critical">Below Threshold</span></td>
            <td>
              <div style={{ display: "flex", gap: "5px" }}>
                <button className="secondary small">Edit</button>
                <button className="primary small">Order</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    {/* Order Actions */}
    <div style={{ marginTop: "25px", display: "flex", gap: "15px", justifyContent: "flex-end" }}>
      <button className="secondary">Export Inventory Data</button>
      <button className="primary">Place Bulk Order</button>
      <button className="primary">Generate Inventory Report</button>
    </div>

    {/* Add CSS for the new elements */}
    <style jsx>{`
      .status-badge {
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
      }
      .in-progress {
        background-color: #fff0f0;
        color: #e53935;
      }
      .testing {
        background-color: #e8f4fd;
        color: #0d6efd;
      }
      .delayed {
        background-color: #fff3e0;
        color: #ff9800;
      }
      .qc {
        background-color: #e0f7fa;
        color: #00bcd4;
      }
      .shipped {
        background-color: #e8f5e9;
        color: #4caf50;
      }
      .blockchain-verified {
        background-color: #e8f5e9;
        color: #4caf50;
        padding: 5px 10px;
        border-radius: 15px;
        font-weight: bold;
      }
      .blockchain-pending {
        background-color: #fff3e0;
        color: #ff9800;
        padding: 5px 10px;
        border-radius: 15px;
        font-weight: bold;
      }
      .inventory-status {
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
      }
      .good {
        background-color: #e8f5e9;
        color: #4caf50;
      }
      .warning {
        background-color: #fff3e0;
        color: #ff9800;
      }
      .critical {
        background-color: #ffebee;
        color: #f44336;
      }
      .filter-dropdown {
        min-width: 150px;
      }
      button.small {
        padding: 5px 10px;
        font-size: 12px;
      }
    `}</style>
  </>
)}

{page === "vendors" && (
  <>
    <div className="header-banner">
      <h2>Vendor Management & Performance</h2>
      <div className="blockchain-indicator">
        {isBlockchainConnected ? 
          <span className="blockchain-connected">⛓️ Blockchain Verification Active</span> : 
          <span className="blockchain-disconnected">⛓️ Connect Wallet for Verification</span>}
      </div>
    </div>

    {/* Vendor Performance Overview */}
    <div className="section-header">
      <h3>Vendor Performance Overview</h3>
    </div>
    
    <div className="kpi-row">
      <div className="kpi-card">
        <h3>Total Vendors</h3>
        <div className="kpi-value">32</div>
        <div className="kpi-subtitle">24 Blockchain Verified</div>
      </div>
      <div className="kpi-card">
        <h3>Avg. On-time Delivery</h3>
        <div className="kpi-value">92.3%</div>
        <div className="kpi-subtitle">+2.1% from last quarter</div>
      </div>
      <div className="kpi-card">
        <h3>Avg. Quality Score</h3>
        <div className="kpi-value">4.7/5</div>
        <div className="kpi-subtitle">Based on 128 reviews</div>
      </div>
      <div className="kpi-card">
        <h3>Active Contracts</h3>
        <div className="kpi-value">37</div>
        <div className="kpi-subtitle">Total value: $12.8M</div>
      </div>
    </div>

    {/* Performance Charts */}
    <div className="charts-grid" style={{ marginTop: "20px" }}>
      <div className="chart-container large">
        <h3>Vendor Performance Metrics (Last 6 Months)</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={vendorPerformanceData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="onTime" stroke="#8884d8" name="On-time Delivery %" />
            <Line type="monotone" dataKey="quality" stroke="#82ca9d" name="Quality Score" />
            <Line type="monotone" dataKey="blockchain" stroke="#ffc658" name="Blockchain Verified %" />
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      <div className="chart-container">
        <h3>Lead Time Comparison</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={leadTimeData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="vendor" />
            <YAxis label={{ value: 'Days', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Bar dataKey="quoted" fill="#8884d8" name="Quoted Lead Time" />
            <Bar dataKey="actual" fill="#82ca9d" name="Actual Lead Time" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      <div className="chart-container">
        <h3>Supplier Location Distribution</h3>
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={supplierDistributionData}
              cx="50%"
              cy="50%"
              labelLine={true}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
              nameKey="name"
              label={({name, percent}) => `${name}: ${(percent * 100).toFixed(0)}%`}
            >
              {supplierDistributionData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'][index % 5]} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => `${value}%`} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>

    {/* Vendor Search and Filter */}
    <div className="section-header">
      <h3>Vendor Directory</h3>
    </div>
    
    <div className="vendor-controls" style={{ marginBottom: "20px", display: "flex", gap: "15px", alignItems: "center" }}>
      <input type="text" placeholder="Search vendors..." style={{ flex: "1" }} />
      <select className="filter-dropdown" style={{ padding: "8px", borderRadius: "5px", border: "1px solid #ccc" }}>
        <option>All Regions</option>
        <option>West Coast</option>
        <option>Midwest</option>
        <option>East Coast</option>
        <option>South</option>
        <option>International</option>
      </select>
      <select className="filter-dropdown" style={{ padding: "8px", borderRadius: "5px", border: "1px solid #ccc" }}>
        <option>All Certifications</option>
        <option>ISO 9001</option>
        <option>AS9100</option>
        <option>ISO 14001</option>
        <option>NADCAP</option>
      </select>
      <select className="filter-dropdown" style={{ padding: "8px", borderRadius: "5px", border: "1px solid #ccc" }}>
        <option>All Blockchain Status</option>
        <option>Verified</option>
        <option>Pending</option>
        <option>Not Verified</option>
      </select>
      <button className="primary">Filter</button>
    </div>

    {/* Vendor Listing Table */}
    <div className="data-table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th>Vendor Name</th>
            <th>Location</th>
            <th>Performance Rating</th>
            <th>Active Contracts</th>
            <th>Specialization</th>
            <th>Lead Time (Avg)</th>
            <th>Blockchain Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><a href="#" onClick={(e) => { e.preventDefault(); setSelectedVendor(vendors[0]); }}>AeroTech Industries</a></td>
            <td>Seattle, WA</td>
            <td>
              <div className="rating-display">
                <div className="stars">★★★★★</div>
                <span>4.8</span>
              </div>
            </td>
            <td>12</td>
            <td>Precision Metal Components, Turbine Components</td>
            <td>14 days</td>
            <td><span className="blockchain-verified">✓ Verified</span></td>
            <td>
              <div className="action-buttons">
                <button className="secondary small">View Profile</button>
                <button className="primary small">Place Order</button>
              </div>
            </td>
          </tr>
          <tr>
            <td><a href="#" onClick={(e) => { e.preventDefault(); setSelectedVendor(vendors[1]); }}>TitaniumPro Supplies</a></td>
            <td>Phoenix, AZ</td>
            <td>
              <div className="rating-display">
                <div className="stars">★★★★★</div>
                <span>4.5</span>
              </div>
            </td>
            <td>8</td>
            <td>Titanium Alloys, Heat-Resistant Materials</td>
            <td>18 days</td>
            <td><span className="blockchain-verified">✓ Verified</span></td>
            <td>
              <div className="action-buttons">
                <button className="secondary small">View Profile</button>
                <button className="primary small">Place Order</button>
              </div>
            </td>
          </tr>
          <tr>
            <td><a href="#" onClick={(e) => { e.preventDefault(); setSelectedVendor(vendors[2]); }}>Global Aero Components</a></td>
            <td>Dallas, TX</td>
            <td>
              <div className="rating-display">
                <div className="stars">★★★★☆</div>
                <span>4.2</span>
              </div>
            </td>
            <td>5</td>
            <td>Landing Gear Systems, Structural Components</td>
            <td>21 days</td>
            <td><span className="blockchain-verified">✓ Verified</span></td>
            <td>
              <div className="action-buttons">
                <button className="secondary small">View Profile</button>
                <button className="primary small">Place Order</button>
              </div>
            </td>
          </tr>
          <tr>
            <td><a href="#" onClick={(e) => { e.preventDefault(); setSelectedVendor(vendors[3]); }}>Precision Aerospace</a></td>
            <td>Boston, MA</td>
            <td>
              <div className="rating-display">
                <div className="stars">★★★★★</div>
                <span>4.7</span>
              </div>
            </td>
            <td>3</td>
            <td>Avionics Components, Electronic Systems</td>
            <td>16 days</td>
            <td><span className="blockchain-pending">⏳ Pending</span></td>
            <td>
              <div className="action-buttons">
                <button className="secondary small">View Profile</button>
                <button className="primary small">Place Order</button>
              </div>
            </td>
          </tr>
          <tr>
            <td><a href="#" onClick={(e) => { e.preventDefault(); }}>SkyHigh Materials</a></td>
            <td>Denver, CO</td>
            <td>
              <div className="rating-display">
                <div className="stars">★★★★☆</div>
                <span>4.1</span>
              </div>
            </td>
            <td>2</td>
            <td>Composite Materials, Carbon Fiber Structures</td>
            <td>25 days</td>
            <td><span className="blockchain-verified">✓ Verified</span></td>
            <td>
              <div className="action-buttons">
                <button className="secondary small">View Profile</button>
                <button className="primary small">Place Order</button>
              </div>
            </td>
          </tr>
          <tr>
            <td><a href="#" onClick={(e) => { e.preventDefault(); }}>JetStream Engineering</a></td>
            <td>Portland, OR</td>
            <td>
              <div className="rating-display">
                <div className="stars">★★★★☆</div>
                <span>4.3</span>
              </div>
            </td>
            <td>4</td>
            <td>Engine Components, Hydraulic Systems</td>
            <td>19 days</td>
            <td><span className="blockchain-not-verified">✗ Not Verified</span></td>
            <td>
              <div className="action-buttons">
                <button className="secondary small">View Profile</button>
                <button className="primary small">Place Order</button>
              </div>
            </td>
          </tr>
          <tr>
            <td><a href="#" onClick={(e) => { e.preventDefault(); }}>AeroMaxx Solutions</a></td>
            <td>Austin, TX</td>
            <td>
              <div className="rating-display">
                <div className="stars">★★★★☆</div>
                <span>4.4</span>
              </div>
            </td>
            <td>3</td>
            <td>Lightweight Alloys, Fastening Systems</td>
            <td>15 days</td>
            <td><span className="blockchain-verified">✓ Verified</span></td>
            <td>
              <div className="action-buttons">
                <button className="secondary small">View Profile</button>
                <button className="primary small">Place Order</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    {/* Recent Performance Reviews */}
    <div className="section-header">
      <h3>Recent Vendor Performance Reviews</h3>
    </div>
    
    <div className="reviews-container" style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "20px", marginBottom: "30px" }}>
      <div className="review-card" style={{ backgroundColor: "white", padding: "20px", borderRadius: "10px", boxShadow: "0 4px 8px rgba(0, 0, 0, 0.08)" }}>
        <div className="review-header" style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}>
          <span style={{ fontWeight: "bold" }}>AeroTech Industries</span>
          <div className="rating-display">
            <div className="stars" style={{ color: "#ffc107" }}>★★★★★</div>
          </div>
        </div>
        <p>"Exceptional quality and consistently on time with deliveries. Their turbofan blades exceeded our specifications."</p>
        <div className="review-footer" style={{ display: "flex", justifyContent: "space-between", marginTop: "10px", fontSize: "12px", color: "#666" }}>
          <span>Order #ORD-2025-0987</span>
          <span>April 2, 2025</span>
        </div>
      </div>
      
      <div className="review-card" style={{ backgroundColor: "white", padding: "20px", borderRadius: "10px", boxShadow: "0 4px 8px rgba(0, 0, 0, 0.08)" }}>
        <div className="review-header" style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}>
          <span style={{ fontWeight: "bold" }}>TitaniumPro Supplies</span>
          <div className="rating-display">
            <div className="stars" style={{ color: "#ffc107" }}>★★★★☆</div>
          </div>
        </div>
        <p>"Great materials and good communication throughout the order process. Delivery was a few days late but they kept us informed."</p>
        <div className="review-footer" style={{ display: "flex", justifyContent: "space-between", marginTop: "10px", fontSize: "12px", color: "#666" }}>
          <span>Order #ORD-2025-0953</span>
          <span>March 28, 2025</span>
        </div>
      </div>
      
      <div className="review-card" style={{ backgroundColor: "white", padding: "20px", borderRadius: "10px", boxShadow: "0 4px 8px rgba(0, 0, 0, 0.08)" }}>
        <div className="review-header" style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}>
          <span style={{ fontWeight: "bold" }}>Precision Aerospace</span>
          <div className="rating-display">
            <div className="stars" style={{ color: "#ffc107" }}>★★★★★</div>
          </div>
        </div>
        <p>"The heat sinks we ordered were perfectly machined and arrived ahead of schedule. Documentation was thorough and blockchain verified."</p>
        <div className="review-footer" style={{ display: "flex", justifyContent: "space-between", marginTop: "10px", fontSize: "12px", color: "#666" }}>
          <span>Order #ORD-2025-0921</span>
          <span>March 25, 2025</span>
        </div>
      </div>
    </div>

    {/* Actions Row */}
    <div style={{ display: "flex", justifyContent: "space-between", marginTop: "20px" }}>
      <button className="secondary">Export Vendor Performance Data</button>
      <div>
        <button className="secondary" style={{ marginRight: "10px" }}>Vendor Onboarding</button>
        <button className="primary">Add New Vendor</button>
      </div>
    </div>

    {/* CSS for new components */}
    <style jsx>{`
      .rating-display {
        display: flex;
        align-items: center;
        gap: 5px;
      }
      .stars {
        color: #ffc107;
        letter-spacing: -2px;
      }
      .blockchain-verified {
        background-color: #e8f5e9;
        color: #4caf50;
        padding: 5px 10px;
        border-radius: 15px;
        font-weight: bold;
        display: inline-block;
        font-size: 12px;
      }
      .blockchain-pending {
        background-color: #fff3e0;
        color: #ff9800;
        padding: 5px 10px;
        border-radius: 15px;
        font-weight: bold;
        display: inline-block;
        font-size: 12px;
      }
      .blockchain-not-verified {
        background-color: #ffebee;
        color: #f44336;
        padding: 5px 10px;
        border-radius: 15px;
        font-weight: bold;
        display: inline-block;
        font-size: 12px;
      }
      .action-buttons {
        display: flex;
        gap: 5px;
      }
      button.small {
        padding: 5px 10px;
        font-size: 12px;
      }
      .filter-dropdown {
        min-width: 150px;
      }
    `}</style>
    
    {/* Vendor Modal */}
    {selectedVendor && (
      <div className="modal-overlay">
        <div className="modal-content-wide">
          <div className="vendor-profile">
            <div className="vendor-header">
              <h2>{selectedVendor.name}</h2>
              {selectedVendor.blockchain ? 
                <div className="blockchain-badge">⛓️ Blockchain Verified</div> : 
                <div className="blockchain-badge" style={{ backgroundColor: "#fff3e0", color: "#ff9800" }}>⛓️ Verification Pending</div>}
            </div>
            
            <div className="vendor-rating">
              <div className="rating-stars">{"★".repeat(Math.floor(selectedVendor.rating))}{"☆".repeat(5 - Math.floor(selectedVendor.rating))}</div>
              <div className="rating-value">{selectedVendor.rating}/5.0</div>
            </div>
            
            <div className="vendor-details">
              <div className="detail-group">
                <h3>Company Information</h3>
                <p><strong>Location:</strong> {selectedVendor.location}</p>
                <p><strong>Active Contracts:</strong> {selectedVendor.activeContracts}</p>
                <p><strong>Contact Person:</strong> {selectedVendor.contactPerson}</p>
                <p><strong>Email:</strong> {selectedVendor.email}</p>
                <p><strong>Phone:</strong> {selectedVendor.phone}</p>
              </div>
              
              <div className="detail-group">
                <h3>Performance Metrics</h3>
                <p><strong>Delivery Performance:</strong> {selectedVendor.deliveryPerformance}%</p>
                <p><strong>Quality Score:</strong> {selectedVendor.qualityScore}/100</p>
                <p><strong>Average Lead Time:</strong> {selectedVendor.avgLeadTime} days</p>
                <p><strong>Last Order Date:</strong> March 15, 2025</p>
                <p><strong>Certifications:</strong> ISO 9001, AS9100</p>
              </div>
            </div>
            
            <div className="vendor-chart-container">
              <h3>Performance History</h3>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={[
                  { month: 'Nov', onTime: Math.floor(Math.random() * 10) + 85, quality: Math.floor(Math.random() * 10) + 80 },
                  { month: 'Dec', onTime: Math.floor(Math.random() * 10) + 85, quality: Math.floor(Math.random() * 10) + 80 },
                  { month: 'Jan', onTime: Math.floor(Math.random() * 10) + 85, quality: Math.floor(Math.random() * 10) + 80 },
                  { month: 'Feb', onTime: Math.floor(Math.random() * 10) + 85, quality: Math.floor(Math.random() * 10) + 80 },
                  { month: 'Mar', onTime: Math.floor(Math.random() * 10) + 85, quality: Math.floor(Math.random() * 10) + 80 },
                  { month: 'Apr', onTime: selectedVendor.deliveryPerformance, quality: selectedVendor.qualityScore }
                ]} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="onTime" stroke="#8884d8" name="On-time Delivery %" />
                  <Line type="monotone" dataKey="quality" stroke="#82ca9d" name="Quality Score" />
                </LineChart>
              </ResponsiveContainer>
            </div>
            
            <div className="section-header">
              <h3>Current Orders</h3>
            </div>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Order ID</th>
                  <th>Part Name</th>
                  <th>Quantity</th>
                  <th>Order Date</th>
                  <th>Delivery Date</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>#ORD-2025-1042</td>
                  <td>Turbofan Blade</td>
                  <td>500</td>
                  <td>Apr 1, 2025</td>
                  <td>Apr 20, 2025</td>
                  <td><span className="status-badge in-progress">In Production</span></td>
                </tr>
                <tr>
                  <td>#ORD-2025-0987</td>
                  <td>Servo Bracket Assembly</td>
                  <td>250</td>
                  <td>Mar 18, 2025</td>
                  <td>Apr 8, 2025</td>
                  <td><span className="status-badge shipped">Shipped</span></td>
                </tr>
              </tbody>
            </table>
            
            <div className="modal-actions" style={{ marginTop: "25px" }}>
              <button className="secondary" onClick={() => setSelectedVendor(null)}>Close</button>
              <div>
                <button className="secondary" style={{ marginRight: "10px" }}>Contact Vendor</button>
                <button className="primary">Place New Order</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    )}
  </>
)}

{page === "vendor-control" && subPage === "bids" && (
  <>
    <div className="header-banner">
      <h2>Vendor Bid Management</h2>
      <div className="blockchain-indicator">
        {isBlockchainConnected ? 
          <span className="blockchain-connected">⛓️ Blockchain Verification Active</span> : 
          <span className="blockchain-disconnected">⛓️ Connect Wallet for Verification</span>}
      </div>
    </div>

    {/* Summary Stats */}
    <div className="kpi-row">
      <div className="kpi-card">
        <h3>Open RFQs</h3>
        <div className="kpi-value">12</div>
        <div className="kpi-subtitle">Total value: $3.2M</div>
      </div>
      <div className="kpi-card">
        <h3>Active Bids</h3>
        <div className="kpi-value">28</div>
        <div className="kpi-subtitle">From 16 vendors</div>
      </div>
      <div className="kpi-card">
        <h3>Pending Approval</h3>
        <div className="kpi-value">7</div>
        <div className="kpi-subtitle">Value: $820K</div>
      </div>
      <div className="kpi-card">
        <h3>Avg. Cost Savings</h3>
        <div className="kpi-value">14.3%</div>
        <div className="kpi-subtitle">vs. previous quarter</div>
      </div>
    </div>

    {/* Actions Bar */}
    <div className="actions-bar" style={{ display: "flex", justifyContent: "space-between", margin: "20px 0" }}>
      <div className="left-actions">
        <button className="primary" style={{ marginRight: "10px" }}>Create New RFQ</button>
        <button className="secondary" style={{ marginRight: "10px" }}>Bulk Upload RFQs</button>
      </div>
      <div className="right-actions">
        <select className="filter-dropdown" style={{ padding: "8px", borderRadius: "5px", border: "1px solid #ccc", marginRight: "10px" }}>
          <option>All RFQ Status</option>
          <option>Open</option>
          <option>Closed</option>
          <option>Awarded</option>
        </select>
        <button className="secondary">Export Bids Data</button>
      </div>
    </div>

    {/* Tabs for different bid views */}
    <div className="bid-tabs" style={{ display: "flex", borderBottom: "1px solid #e0e0e0", marginBottom: "20px" }}>
      <div className="tab active" style={{ padding: "10px 20px", cursor: "pointer", borderBottom: "2px solid #e53935", color: "#e53935", fontWeight: "bold" }}>Active RFQs</div>
      <div className="tab" style={{ padding: "10px 20px", cursor: "pointer" }}>Submitted Bids</div>
      <div className="tab" style={{ padding: "10px 20px", cursor: "pointer" }}>Awarded Contracts</div>
      <div className="tab" style={{ padding: "10px 20px", cursor: "pointer" }}>Archived RFQs</div>
    </div>

    {/* Active RFQs Section */}
    <div className="section-header">
      <h3>Active RFQs</h3>
    </div>

    <div className="data-table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th>RFQ ID</th>
            <th>Material/Part</th>
            <th>Quantity</th>
            <th>Date Posted</th>
            <th>Closing Date</th>
            <th>Status</th>
            <th>Blockchain Status</th>
            <th>Bids</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><a href="#" onClick={(e) => e.preventDefault()}>RFQ-2025-042</a></td>
            <td>Turbofan Blade</td>
            <td>500 units</td>
            <td>Apr 01, 2025</td>
            <td>Apr 15, 2025</td>
            <td><span className="status-badge open">Open</span></td>
            <td><span className="blockchain-verified">✓ Verified</span></td>
            <td>3 bids</td>
            <td>
              <div className="action-buttons">
                <button className="secondary small">View Bids</button>
                <button className="primary small">Compare</button>
              </div>
            </td>
          </tr>
          <tr>
            <td><a href="#" onClick={(e) => e.preventDefault()}>RFQ-2025-039</a></td>
            <td>Actuator Arm</td>
            <td>300 units</td>
            <td>Mar 28, 2025</td>
            <td>Apr 11, 2025</td>
            <td><span className="status-badge open">Open</span></td>
            <td><span className="blockchain-verified">✓ Verified</span></td>
            <td>5 bids</td>
            <td>
              <div className="action-buttons">
                <button className="secondary small">View Bids</button>
                <button className="primary small">Compare</button>
              </div>
            </td>
          </tr>
          <tr>
            <td><a href="#" onClick={(e) => e.preventDefault()}>RFQ-2025-035</a></td>
            <td>Landing Gear Shaft</td>
            <td>150 units</td>
            <td>Mar 25, 2025</td>
            <td>Apr 08, 2025</td>
            <td><span className="status-badge closing">Closing Soon</span></td>
            <td><span className="blockchain-verified">✓ Verified</span></td>
            <td>2 bids</td>
            <td>
              <div className="action-buttons">
                <button className="secondary small">View Bids</button>
                <button className="primary small">Compare</button>
              </div>
            </td>
          </tr>
          <tr>
            <td><a href="#" onClick={(e) => e.preventDefault()}>RFQ-2025-030</a></td>
            <td>Avionics Heat Sink</td>
            <td>800 units</td>
            <td>Mar 20, 2025</td>
            <td>Apr 10, 2025</td>
            <td><span className="status-badge open">Open</span></td>
            <td><span className="blockchain-pending">⏳ Pending</span></td>
            <td>4 bids</td>
            <td>
              <div className="action-buttons">
                <button className="secondary small">View Bids</button>
                <button className="primary small">Compare</button>
              </div>
            </td>
          </tr>
          <tr>
            <td><a href="#" onClick={(e) => e.preventDefault()}>RFQ-2025-028</a></td>
            <td>Composite Fuselage Panel</td>
            <td>200 units</td>
            <td>Mar 18, 2025</td>
            <td>Apr 04, 2025</td>
            <td><span className="status-badge reviewing">Under Review</span></td>
            <td><span className="blockchain-verified">✓ Verified</span></td>
            <td>6 bids</td>
            <td>
              <div className="action-buttons">
                <button className="secondary small">View Bids</button>
                <button className="primary small">Compare</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    {/* Bid Comparison Modal (dummy/preview) */}
    <div className="section-header" style={{ marginTop: "30px" }}>
      <h3>Bid Comparison: Turbofan Blade (RFQ-2025-042)</h3>
    </div>
    
    <div className="comparison-container" style={{ backgroundColor: "white", padding: "20px", borderRadius: "10px", boxShadow: "0 4px 8px rgba(0, 0, 0, 0.08)", marginBottom: "30px" }}>
      <div className="data-table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Vendor</th>
              <th>Bid Price</th>
              <th>Unit Price</th>
              <th>Lead Time</th>
              <th>Payment Terms</th>
              <th>Quality Certification</th>
              <th>Vendor Rating</th>
              <th>Blockchain Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr style={{ backgroundColor: "#fff0f0" }}>
              <td>AeroTech Industries</td>
              <td><strong>$160,000</strong></td>
              <td>$320/unit</td>
              <td>14 days</td>
              <td>Net 30</td>
              <td>ISO 9001, AS9100</td>
              <td>
                <div className="rating-display">
                  <div className="stars" style={{ color: "#ffc107" }}>★★★★★</div>
                  <span>4.8</span>
                </div>
              </td>
              <td><span className="blockchain-verified">✓ Verified</span></td>
              <td>
                <button className="primary small">Award</button>
              </td>
            </tr>
            <tr>
              <td>TitaniumPro Supplies</td>
              <td>$172,500</td>
              <td>$345/unit</td>
              <td>18 days</td>
              <td>Net 45</td>
              <td>ISO 9001</td>
              <td>
                <div className="rating-display">
                  <div className="stars" style={{ color: "#ffc107" }}>★★★★☆</div>
                  <span>4.5</span>
                </div>
              </td>
              <td><span className="blockchain-verified">✓ Verified</span></td>
              <td>
                <button className="primary small">Award</button>
              </td>
            </tr>
            <tr>
              <td>Global Aero Components</td>
              <td>$185,000</td>
              <td>$370/unit</td>
              <td>12 days</td>
              <td>Net 30</td>
              <td>ISO 9001, AS9100</td>
              <td>
                <div className="rating-display">
                  <div className="stars" style={{ color: "#ffc107" }}>★★★★☆</div>
                  <span>4.2</span>
                </div>
              </td>
              <td><span className="blockchain-verified">✓ Verified</span></td>
              <td>
                <button className="primary small">Award</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div className="comparison-charts" style={{ display: "flex", marginTop: "20px", gap: "20px" }}>
        <div className="chart-container" style={{ flex: "1" }}>
          <h4>Price Comparison</h4>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={[
              { name: 'AeroTech', price: 320 },
              { name: 'TitaniumPro', price: 345 },
              { name: 'Global Aero', price: 370 }
            ]} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis label={{ value: 'Unit Price ($)', angle: -90, position: 'insideLeft' }} />
              <Tooltip formatter={(value) => [`$${value}`, 'Unit Price']} />
              <Bar dataKey="price" fill="#e53935" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        <div className="chart-container" style={{ flex: "1" }}>
          <h4>Lead Time Comparison</h4>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={[
              { name: 'AeroTech', days: 14 },
              { name: 'TitaniumPro', days: 18 },
              { name: 'Global Aero', days: 12 }
            ]} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis label={{ value: 'Days', angle: -90, position: 'insideLeft' }} />
              <Tooltip formatter={(value) => [`${value} days`, 'Lead Time']} />
              <Bar dataKey="days" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      <div className="comparison-actions" style={{ display: "flex", justifyContent: "space-between", marginTop: "20px" }}>
        <button className="secondary">Export Comparison</button>
        <div>
          <button className="secondary" style={{ marginRight: "10px" }}>Request Additional Information</button>
          <button className="primary">Award Selected Bid</button>
        </div>
      </div>
    </div>

    {/* Recent Activity Section */}
    <div className="section-header">
      <h3>Recent Bid Activity</h3>
    </div>
    
    <div className="activity-timeline" style={{ backgroundColor: "white", padding: "20px", borderRadius: "10px", boxShadow: "0 4px 8px rgba(0, 0, 0, 0.08)" }}>
      <div className="timeline-item" style={{ borderLeft: "2px solid #e53935", paddingLeft: "20px", position: "relative", marginBottom: "20px" }}>
        <div className="timeline-dot" style={{ position: "absolute", left: "-10px", top: "0", width: "18px", height: "18px", backgroundColor: "#e53935", borderRadius: "50%" }}></div>
        <div className="timeline-content">
          <div className="timeline-header" style={{ display: "flex", justifyContent: "space-between" }}>
            <span style={{ fontWeight: "bold" }}>New Bid Received</span>
            <span style={{ color: "#666", fontSize: "14px" }}>April 5, 2025 - 10:32 AM</span>
          </div>
          <p>TitaniumPro Supplies submitted a bid for RFQ-2025-042 (Turbofan Blade). <a href="#">View Details</a></p>
        </div>
      </div>
      
      <div className="timeline-item" style={{ borderLeft: "2px solid #e53935", paddingLeft: "20px", position: "relative", marginBottom: "20px" }}>
        <div className="timeline-dot" style={{ position: "absolute", left: "-10px", top: "0", width: "18px", height: "18px", backgroundColor: "#e53935", borderRadius: "50%" }}></div>
        <div className="timeline-content">
          <div className="timeline-header" style={{ display: "flex", justifyContent: "space-between" }}>
            <span style={{ fontWeight: "bold" }}>RFQ Created</span>
            <span style={{ color: "#666", fontSize: "14px" }}>April 4, 2025 - 3:15 PM</span>
          </div>
          <p>New RFQ-2025-044 created for High-Precision Gearbox (100 units). <a href="#">View RFQ</a></p>
        </div>
      </div>
      
      <div className="timeline-item" style={{ borderLeft: "2px solid #e53935", paddingLeft: "20px", position: "relative", marginBottom: "20px" }}>
        <div className="timeline-dot" style={{ position: "absolute", left: "-10px", top: "0", width: "18px", height: "18px", backgroundColor: "#e53935", borderRadius: "50%" }}></div>
        <div className="timeline-content">
          <div className="timeline-header" style={{ display: "flex", justifyContent: "space-between" }}>
            <span style={{ fontWeight: "bold" }}>Bid Awarded</span>
            <span style={{ color: "#666", fontSize: "14px" }}>April 3, 2025 - 11:47 AM</span>
          </div>
          <p>Contract awarded to Precision Aerospace for RFQ-2025-027 (Avionics Cooling System). <a href="#">View Contract</a></p>
        </div>
      </div>
      
      <div className="timeline-item" style={{ borderLeft: "2px solid #e53935", paddingLeft: "20px", position: "relative" }}>
        <div className="timeline-dot" style={{ position: "absolute", left: "-10px", top: "0", width: "18px", height: "18px", backgroundColor: "#e53935", borderRadius: "50%" }}></div>
        <div className="timeline-content">
          <div className="timeline-header" style={{ display: "flex", justifyContent: "space-between" }}>
            <span style={{ fontWeight: "bold" }}>RFQ Updated</span>
            <span style={{ color: "#666", fontSize: "14px" }}>April 2, 2025 - 9:23 AM</span>
          </div>
          <p>Specifications updated for RFQ-2025-035 (Landing Gear Shaft). <a href="#">View Changes</a></p>
        </div>
      </div>
    </div>

    {/* CSS for new components */}
    <style jsx>{`
      .status-badge {
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
      }
      .open {
        background-color: #e8f5e9;
        color: #4caf50;
      }
      .closing {
        background-color: #fff3e0;
        color: #ff9800;
      }
      .reviewing {
        background-color: #e3f2fd;
        color: #2196f3;
      }
      .blockchain-verified {
        background-color: #e8f5e9;
        color: #4caf50;
        padding: 5px 10px;
        border-radius: 15px;
        font-weight: bold;
        display: inline-block;
        font-size: 12px;
      }
      .blockchain-pending {
        background-color: #fff3e0;
        color: #ff9800;
        padding: 5px 10px;
        border-radius: 15px;
        font-weight: bold;
        display: inline-block;
        font-size: 12px;
      }
      .action-buttons {
        display: flex;
        gap: 5px;
      }
      button.small {
        padding: 5px 10px;
        font-size: 12px;
      }
      .filter-dropdown {
        min-width: 150px;
      }
      .rating-display {
        display: flex;
        align-items: center;
        gap: 5px;
      }
      .stars {
        color: #ffc107;
        letter-spacing: -2px;
      }
    `}</style>
  </>
)}

        {page === "vendor-control" && subPage === "followups" && (
          <>
            <h2>Vendor Follow-Ups</h2>
            <p>Set follow-up reminders and track vendor updates:</p>
            <table>
              <thead>
                <tr><th>Vendor</th><th>Material</th><th>Next Update</th><th>Status</th><th>Blockchain Contract</th></tr>
              </thead>
              <tbody>
                <tr>
                  <td>Vendor A</td>
                  <td>Titanium Alloy</td>
                  <td>April 15, 2025</td>
                  <td>Pending</td>
                  <td><code>0x12...3f4d</code></td>
                </tr>
                <tr>
                  <td>Vendor B</td>
                  <td>Aluminum 7075</td>
                  <td>April 18, 2025</td>
                  <td>Scheduled</td>
                  <td><code>0x78...9a2b</code></td>
                </tr>
              </tbody>
            </table>
          </>
        )}

{page === "vendor-control" && subPage === "trusted" && (
  <>
    <div className="header-banner">
      <h2>Trusted Vendor Sources</h2>
      <div className="blockchain-indicator">
        {isBlockchainConnected ? 
          <span className="blockchain-connected">⛓️ Blockchain Verification Active</span> : 
          <span className="blockchain-disconnected">⛓️ Connect Wallet for Verification</span>}
      </div>
    </div>

    {/* Summary Stats */}
    <div className="kpi-row">
      <div className="kpi-card">
        <h3>Verified Sources</h3>
        <div className="kpi-value">24</div>
        <div className="kpi-subtitle">100% blockchain certified</div>
      </div>
      <div className="kpi-card">
        <h3>Avg. Trust Score</h3>
        <div className="kpi-value">92.7</div>
        <div className="kpi-subtitle">+2.3 from Q1</div>
      </div>
      <div className="kpi-card">
        <h3>Active Trusted Contracts</h3>
        <div className="kpi-value">18</div>
        <div className="kpi-subtitle">Total value: $8.2M</div>
      </div>
      <div className="kpi-card">
        <h3>Pending Verification</h3>
        <div className="kpi-value">5</div>
        <div className="kpi-subtitle">Est. completion: 7 days</div>
      </div>
    </div>

    {/* Trust Score Chart */}
    <div className="section-header" style={{ marginTop: "20px" }}>
      <h3>Trust Score Analytics</h3>
    </div>
    <div className="trust-analytics" style={{ backgroundColor: "white", padding: "20px", borderRadius: "10px", boxShadow: "0 4px 8px rgba(0, 0, 0, 0.08)", marginBottom: "30px" }}>
      <div className="charts-grid" style={{ display: "grid", gridTemplateColumns: "3fr 2fr", gap: "20px" }}>
        <div className="chart-container">
          <h4 style={{ margin: "0 0 15px 0" }}>Trust Score Progression (Last 6 Months)</h4>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={[
              { month: 'Nov', score: 89.5, industry: 85.0 },
              { month: 'Dec', score: 90.1, industry: 85.5 },
              { month: 'Jan', score: 90.8, industry: 86.2 },
              { month: 'Feb', score: 91.4, industry: 86.8 },
              { month: 'Mar', score: 92.1, industry: 87.3 },
              { month: 'Apr', score: 92.7, industry: 87.9 }
            ]} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis domain={[80, 100]} label={{ value: 'Score', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="score" stroke="#e53935" name="Your Trusted Vendors" strokeWidth={2} />
              <Line type="monotone" dataKey="industry" stroke="#9e9e9e" name="Industry Average" strokeDasharray="5 5" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-container">
          <h4 style={{ margin: "0 0 15px 0" }}>Trust Score Components</h4>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart layout="vertical" data={[
              { name: 'Quality', score: 94.5 },
              { name: 'Delivery', score: 93.2 },
              { name: 'Blockchain Compliance', score: 97.8 },
              { name: 'Documentation', score: 89.5 },
              { name: 'Cost Transparency', score: 88.6 }
            ]} margin={{ top: 5, right: 30, left: 50, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[80, 100]} />
              <YAxis dataKey="name" type="category" />
              <Tooltip formatter={(value) => [`${value}`, 'Score']} />
              <Bar dataKey="score" fill="#e53935" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>

    {/* Controls and Search */}
    <div className="filter-controls" style={{ display: "flex", justifyContent: "space-between", marginBottom: "20px" }}>
      <div className="search-box" style={{ flex: "1", marginRight: "15px" }}>
        <input 
          type="text" 
          placeholder="Search trusted vendors..." 
          style={{ 
            width: "100%", 
            padding: "10px 15px", 
            borderRadius: "5px", 
            border: "1px solid #ddd",
            fontSize: "14px"
          }} 
        />
      </div>
      <div className="right-controls" style={{ display: "flex", gap: "10px" }}>
        <select className="filter-dropdown" style={{ padding: "10px", borderRadius: "5px", border: "1px solid #ddd" }}>
          <option>All Categories</option>
          <option>Manufacturing</option>
          <option>Raw Materials</option>
          <option>Component Suppliers</option>
          <option>Services</option>
        </select>
        <select className="filter-dropdown" style={{ padding: "10px", borderRadius: "5px", border: "1px solid #ddd" }}>
          <option>All Locations</option>
          <option>Domestic</option>
          <option>International</option>
          <option>West Coast</option>
          <option>East Coast</option>
        </select>
        <button className="primary">
          <span>Add New Trusted Vendor</span>
        </button>
      </div>
    </div>

    {/* Trusted Vendors Table */}
    <div className="section-header">
      <h3>Verified Trusted Vendors</h3>
    </div>
    <div className="data-table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th>Vendor Name</th>
            <th>Category</th>
            <th>Location</th>
            <th>Trust Score</th>
            <th>Certification</th>
            <th>Blockchain Verification</th>
            <th>Last Audit</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>
              <div style={{ display: "flex", alignItems: "center" }}>
                <div style={{ width: "8px", height: "8px", backgroundColor: "#4caf50", borderRadius: "50%", marginRight: "10px" }}></div>
                <span>AeroTech Industries</span>
              </div>
            </td>
            <td>Manufacturing</td>
            <td>Seattle, WA, USA</td>
            <td>
              <div className="score-bar" style={{ display: "flex", alignItems: "center" }}>
                <div style={{ 
                  width: "100px", 
                  height: "10px", 
                  backgroundColor: "#e0e0e0", 
                  borderRadius: "5px", 
                  overflow: "hidden",
                  marginRight: "10px"
                }}>
                  <div style={{ width: "98%", height: "100%", backgroundColor: "#4caf50" }}></div>
                </div>
                <span>98</span>
              </div>
            </td>
            <td>ISO 9001, AS9100</td>
            <td>
              <div style={{ display: "flex", alignItems: "center" }}>
                <span className="blockchain-verified" style={{ fontSize: "12px" }}>
                  <span className="blockchain-icon">⛓️</span> Verified
                </span>
                <span style={{ marginLeft: "5px", fontFamily: "monospace", fontSize: "12px", color: "#666" }}>
                  0x7Fe3...4d2A
                </span>
              </div>
            </td>
            <td>March 15, 2025</td>
            <td>
              <div className="action-buttons">
                <button className="secondary small">Details</button>
                <button className="primary small">Order</button>
              </div>
            </td>
          </tr>
          <tr>
            <td>
              <div style={{ display: "flex", alignItems: "center" }}>
                <div style={{ width: "8px", height: "8px", backgroundColor: "#4caf50", borderRadius: "50%", marginRight: "10px" }}></div>
                <span>TitaniumPro Supplies</span>
              </div>
            </td>
            <td>Raw Materials</td>
            <td>Phoenix, AZ, USA</td>
            <td>
              <div className="score-bar" style={{ display: "flex", alignItems: "center" }}>
                <div style={{ 
                  width: "100px", 
                  height: "10px", 
                  backgroundColor: "#e0e0e0", 
                  borderRadius: "5px", 
                  overflow: "hidden",
                  marginRight: "10px"
                }}>
                  <div style={{ width: "95%", height: "100%", backgroundColor: "#4caf50" }}></div>
                </div>
                <span>95</span>
              </div>
            </td>
            <td>ISO 9001, ISO 14001</td>
            <td>
              <div style={{ display: "flex", alignItems: "center" }}>
                <span className="blockchain-verified" style={{ fontSize: "12px" }}>
                  <span className="blockchain-icon">⛓️</span> Verified
                </span>
                <span style={{ marginLeft: "5px", fontFamily: "monospace", fontSize: "12px", color: "#666" }}>
                  0x9Ab2...7c3F
                </span>
              </div>
            </td>
            <td>February 28, 2025</td>
            <td>
              <div className="action-buttons">
                <button className="secondary small">Details</button>
                <button className="primary small">Order</button>
              </div>
            </td>
          </tr>
          <tr>
            <td>
              <div style={{ display: "flex", alignItems: "center" }}>
                <div style={{ width: "8px", height: "8px", backgroundColor: "#ff9800", borderRadius: "50%", marginRight: "10px" }}></div>
                <span>Global Aero Components</span>
              </div>
            </td>
            <td>Component Suppliers</td>
            <td>Dallas, TX, USA</td>
            <td>
              <div className="score-bar" style={{ display: "flex", alignItems: "center" }}>
                <div style={{ 
                  width: "100px", 
                  height: "10px", 
                  backgroundColor: "#e0e0e0", 
                  borderRadius: "5px", 
                  overflow: "hidden",
                  marginRight: "10px"
                }}>
                  <div style={{ width: "88%", height: "100%", backgroundColor: "#ff9800" }}></div>
                </div>
                <span>88</span>
              </div>
            </td>
            <td>AS9100, NADCAP</td>
            <td>
              <div style={{ display: "flex", alignItems: "center" }}>
                <span className="blockchain-verified" style={{ fontSize: "12px" }}>
                  <span className="blockchain-icon">⛓️</span> Verified
                </span>
                <span style={{ marginLeft: "5px", fontFamily: "monospace", fontSize: "12px", color: "#666" }}>
                  0x3Df5...9e2B
                </span>
              </div>
            </td>
            <td>March 05, 2025</td>
            <td>
              <div className="action-buttons">
                <button className="secondary small">Details</button>
                <button className="primary small">Order</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    {/* Pending Verification Section */}
    <div className="section-header" style={{ marginTop: "30px" }}>
      <h3>Pending Verification</h3>
    </div>
    <div className="data-table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th>Vendor Name</th>
            <th>Category</th>
            <th>Location</th>
            <th>Initial Score</th>
            <th>Documentation</th>
            <th>Verification Status</th>
            <th>Submitted Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>
              <div style={{ display: "flex", alignItems: "center" }}>
                <div style={{ width: "8px", height: "8px", backgroundColor: "#ff9800", borderRadius: "50%", marginRight: "10px" }}></div>
                <span>Precision Aerospace</span>
              </div>
            </td>
            <td>Manufacturing</td>
            <td>Boston, MA, USA</td>
            <td>
              <div className="score-bar" style={{ display: "flex", alignItems: "center" }}>
                <div style={{ 
                  width: "100px", 
                  height: "10px", 
                  backgroundColor: "#e0e0e0", 
                  borderRadius: "5px", 
                  overflow: "hidden",
                  marginRight: "10px"
                }}>
                  <div style={{ width: "90%", height: "100%", backgroundColor: "#ff9800" }}></div>
                </div>
                <span>90</span>
              </div>
            </td>
            <td>
              <span className="doc-status complete" style={{ backgroundColor: "#e8f5e9", color: "#4caf50", padding: "4px 8px", borderRadius: "15px", fontSize: "12px", fontWeight: "bold" }}>Complete</span>
            </td>
            <td>
              <div className="progress-container">
                <div className="progress-bar" style={{ 
                  width: "150px", 
                  height: "6px", 
                  backgroundColor: "#e0e0e0", 
                  borderRadius: "3px", 
                  overflow: "hidden",
                  marginRight: "10px"
                }}>
                  <div style={{ width: "80%", height: "100%", backgroundColor: "#e53935" }}></div>
                </div>
                <span style={{ fontSize: "12px" }}>80% - Wallet Setup</span>
              </div>
            </td>
            <td>April 2, 2025</td>
            <td>
              <div className="action-buttons">
                <button className="secondary small">Review</button>
                <button className="primary small">Verify</button>
              </div>
            </td>
          </tr>
          <tr>
            <td>
              <div style={{ display: "flex", alignItems: "center" }}>
                <div style={{ width: "8px", height: "8px", backgroundColor: "#f44336", borderRadius: "50%", marginRight: "10px" }}></div>
                <span>JetStream Engineering</span>
              </div>
            </td>
            <td>Component Suppliers</td>
            <td>Portland, OR, USA</td>
            <td>
              <div className="score-bar" style={{ display: "flex", alignItems: "center" }}>
                <div style={{ 
                  width: "100px", 
                  height: "10px", 
                  backgroundColor: "#e0e0e0", 
                  borderRadius: "5px", 
                  overflow: "hidden",
                  marginRight: "10px"
                }}>
                  <div style={{ width: "82%", height: "100%", backgroundColor: "#f44336" }}></div>
                </div>
                <span>82</span>
              </div>
            </td>
            <td>
              <span className="doc-status incomplete" style={{ backgroundColor: "#ffebee", color: "#f44336", padding: "4px 8px", borderRadius: "15px", fontSize: "12px", fontWeight: "bold" }}>Incomplete</span>
            </td>
            <td>
              <div className="progress-container">
                <div className="progress-bar" style={{ 
                  width: "150px", 
                  height: "6px", 
                  backgroundColor: "#e0e0e0", 
                  borderRadius: "3px", 
                  overflow: "hidden",
                  marginRight: "10px"
                }}>
                  <div style={{ width: "20%", height: "100%", backgroundColor: "#e53935" }}></div>
                </div>
                <span style={{ fontSize: "12px" }}>20% - Initial Review</span>
              </div>
            </td>
            <td>April 4, 2025</td>
            <td>
              <div className="action-buttons">
                <button className="secondary small">Review</button>
                <button className="primary small">Request Docs</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    {/* Onboarding Process Section */}
    <div className="section-header" style={{ marginTop: "30px" }}>
      <h3>Blockchain Verification Process</h3>
    </div>
    <div className="process-container" style={{ display: "flex", backgroundColor: "white", padding: "20px", borderRadius: "10px", boxShadow: "0 4px 8px rgba(0, 0, 0, 0.08)", marginBottom: "30px" }}>
      <div className="process-step" style={{ flex: "1", position: "relative", textAlign: "center", padding: "0 15px" }}>
        <div className="step-number" style={{ width: "40px", height: "40px", backgroundColor: "#e53935", color: "white", borderRadius: "50%", display: "flex", justifyContent: "center", alignItems: "center", margin: "0 auto 15px auto", fontWeight: "bold" }}>1</div>
        <div className="step-line" style={{ position: "absolute", top: "20px", right: "-50%", width: "100%", height: "2px", backgroundColor: "#e0e0e0", zIndex: "0" }}></div>
        <h4 style={{ margin: "0 0 10px 0" }}>Documentation</h4>
        <p style={{ fontSize: "14px", color: "#666", margin: "0" }}>Collect and verify all required company documentation and certifications</p>
      </div>
      <div className="process-step" style={{ flex: "1", position: "relative", textAlign: "center", padding: "0 15px" }}>
        <div className="step-number" style={{ width: "40px", height: "40px", backgroundColor: "#e53935", color: "white", borderRadius: "50%", display: "flex", justifyContent: "center", alignItems: "center", margin: "0 auto 15px auto", fontWeight: "bold" }}>2</div>
        <div className="step-line" style={{ position: "absolute", top: "20px", right: "-50%", width: "100%", height: "2px", backgroundColor: "#e0e0e0", zIndex: "0" }}></div>
        <h4 style={{ margin: "0 0 10px 0" }}>Wallet Setup</h4>
        <p style={{ fontSize: "14px", color: "#666", margin: "0" }}>Create and secure blockchain wallet for vendor verification and transactions</p>
      </div>
      <div className="process-step" style={{ flex: "1", position: "relative", textAlign: "center", padding: "0 15px" }}>
        <div className="step-number" style={{ width: "40px", height: "40px", backgroundColor: "#e53935", color: "white", borderRadius: "50%", display: "flex", justifyContent: "center", alignItems: "center", margin: "0 auto 15px auto", fontWeight: "bold" }}>3</div>
        <div className="step-line" style={{ position: "absolute", top: "20px", right: "-50%", width: "100%", height: "2px", backgroundColor: "#e0e0e0", zIndex: "0" }}></div>
        <h4 style={{ margin: "0 0 10px 0" }}>Smart Contract</h4>
        <p style={{ fontSize: "14px", color: "#666", margin: "0" }}>Deploy smart contract with terms, conditions, and verification metrics</p>
      </div>
      <div className="process-step" style={{ flex: "1", position: "relative", textAlign: "center", padding: "0 15px" }}>
        <div className="step-number" style={{ width: "40px", height: "40px", backgroundColor: "#e53935", color: "white", borderRadius: "50%", display: "flex", justifyContent: "center", alignItems: "center", margin: "0 auto 15px auto", fontWeight: "bold" }}>4</div>
        <h4 style={{ margin: "0 0 10px 0" }}>Verification</h4>
        <p style={{ fontSize: "14px", color: "#666", margin: "0" }}>Final verification audit and activation of trusted vendor status</p>
      </div>
    </div>

    {/* Add New Trusted Vendor Form */}
    <div className="section-header" style={{ marginTop: "30px" }}>
      <h3>Add New Trusted Vendor</h3>
    </div>
    <div className="add-vendor-form" style={{ backgroundColor: "white", padding: "25px", borderRadius: "10px", boxShadow: "0 4px 8px rgba(0, 0, 0, 0.08)", marginBottom: "30px" }}>
      <div className="blockchain-note" style={{ backgroundColor: "#fff0f0", borderLeft: "4px solid #e53935", padding: "15px", marginBottom: "20px" }}>
        <p style={{ margin: "0", fontWeight: "bold" }}>⛓️ Blockchain Verification Required</p>
        <p style={{ margin: "10px 0 0 0", fontSize: "14px" }}>All trusted vendors must complete blockchain verification. The vendor will need to provide documentation and create a blockchain wallet for verification.</p>
      </div>
      
      <div className="form-grid" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        <div className="form-group">
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>Vendor Name *</label>
          <input type="text" placeholder="Enter company name" style={{ width: "100%", padding: "10px", borderRadius: "5px", border: "1px solid #ddd" }} />
        </div>
        <div className="form-group">
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>Category *</label>
          <select style={{ width: "100%", padding: "10px", borderRadius: "5px", border: "1px solid #ddd" }}>
            <option>Select a category</option>
            <option>Manufacturing</option>
            <option>Raw Materials</option>
            <option>Component Suppliers</option>
            <option>Services</option>
          </select>
        </div>
        <div className="form-group">
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>Contact Email *</label>
          <input type="email" placeholder="Enter contact email" style={{ width: "100%", padding: "10px", borderRadius: "5px", border: "1px solid #ddd" }} />
        </div>
        <div className="form-group">
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>Phone Number *</label>
          <input type="tel" placeholder="Enter phone number" style={{ width: "100%", padding: "10px", borderRadius: "5px", border: "1px solid #ddd" }} />
        </div>
        <div className="form-group">
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>Location *</label>
          <input type="text" placeholder="City, State, Country" style={{ width: "100%", padding: "10px", borderRadius: "5px", border: "1px solid #ddd" }} />
        </div>
        <div className="form-group">
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>Certifications</label>
          <input type="text" placeholder="e.g., ISO 9001, AS9100" style={{ width: "100%", padding: "10px", borderRadius: "5px", border: "1px solid #ddd" }} />
        </div>
      </div>
      
      <div style={{ marginTop: "25px", borderTop: "1px solid #eee", paddingTop: "20px", display: "flex", justifyContent: "flex-end" }}>
        <button className="secondary" style={{ marginRight: "10px" }}>Cancel</button>
        <button className="primary">Submit for Verification</button>
      </div>
    </div>
    
    {/* CSS for status elements */}
    <style jsx>{`
      .blockchain-verified {
        background-color: #e8f5e9;
        color: #4caf50;
        padding: 5px 10px;
        border-radius: 15px;
        font-weight: bold;
        display: inline-block;
        font-size: 12px;
      }
      .action-buttons {
        display: flex;
        gap: 5px;
      }
      button.small {
        padding: 5px 10px;
        font-size: 12px;
      }
    `}</style>
  </>
)}
export default App;

About AeroChain:
AeroChain is designed to transform aerospace supply chains through digitization. Our platform centralizes fragmented supplier data into a smart, unified hub. It leverages data lakes, blockchain, and AI/ML to drive transparency, predict disruptions, and automate procurement.

Why it matters:
- Supplier delays can cripple timelines and create bottlenecks.
- A centralized system brings real-time insights and smarter sourcing.
- Blockchain ensures traceable, tamper-proof tracking.
- AI predicts delays and bottlenecks before they happen.

App Highlights:
✓ Smart sourcing with real-time performance comparisons  
✓ Blockchain-backed transparency for orders and deliveries  
✓ Automated procurement workflows and quote negotiations  
✓ Predictive insights using AI-driven data  
✓ Supplier accountability and performance improvement tools

Kudos to our awesome team: Sameerjeet, Shyam, Vikrant, Vamshi, Aishwarya, and Vishvali — with gratitude to our mentors Dr. Beth Boardman and Dr. Sangram Redkar.
"""

# Prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages")
])

# Memory store for chat sessions
store = {}
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# LangChain chain setup
chain = (
    RunnablePassthrough.assign(messages=itemgetter("messages"))
    | prompt
    | lang_model
)

with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="messages"
)

# Streamlit UI
st.set_page_config(page_title="Astra – AeroChain AI Guide", layout="centered")
st.title("🚀 Welcome, I am Astra, your AI guide from AeroChain. How can I help you today?")

session_id = "aerochain_orientation"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat display
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box
user_input = st.chat_input("Ask anything about AeroChain's solution or this project...")

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    response = with_history.invoke({
        "messages": [HumanMessage(content=user_input)],
    }, config={"configurable": {"session_id": session_id}})

    st.chat_message("assistant").markdown(response.content)
    st.session_state.chat_history.append({"role": "assistant", "content": response.content})
