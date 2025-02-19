import { Link } from "react-router-dom";
import './Navigation.css';

const Navigation = () => {
  return (
    <nav className="credix-nav">
      <div className="credix-nav-inner">
        <div className="credix-nav-logo">
          <Link to="/">MYSTORE</Link>
        </div>
        <div className="credix-nav-links-container">
          <div className="credix-nav-link">
            <Link to="/">Checkout</Link>
          </div>
          <div className="credix-nav-link">
            <Link to="/about">About</Link>
          </div>
          <div className="credix-nav-link">
            <Link to="/contact">Contact</Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
