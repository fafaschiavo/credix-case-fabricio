import { useState } from 'react';
import { useNavigate } from "react-router-dom";
import './Checkout.css';
import { Typography } from '@mui/material';
import Button from '../../components/Button/Button';
import Card from '../../components/Card/Card';
import TextInput from '../../components/TextInput/TextInput';
import { API_BASE_URL } from '../../constants.ts';
import axios from 'axios';
import toast, { Toaster } from 'react-hot-toast';

// Define types
interface CartItem {
  sku: string;
  name: string;
  price: number;
  quantity: number;
}

interface FormData {
  cnpj: string;
  email: string;
  phone: string;
  firstName: string;
  lastName: string;
  term?: number;
  cart?: CartItem[];
}

interface FormErrors {
  cnpj?: string;
  email?: string;
  phone?: string;
  firstName?: string;
  lastName?: string;
}

const Checkout: React.FC = () => {
  const [cartItems] = useState<CartItem[]>([
    { sku: 'oweuriek', name: "Product A", price: 100, quantity: 1 },
    { sku: 'eepheeje', name: "Product B", price: 150, quantity: 2 },
  ]);

  const [formData, setFormData] = useState<FormData>({
    cnpj: '',
    email: '',
    phone: '',
    firstName: '',
    lastName: ''
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [terms, setTerms] = useState([]);
  const [activeTerm, setActiveTerm] = useState(0);

  const navigate = useNavigate();

  /**
   * Calculates the total price of items in the cart.
   * @returns {number} - The total cost.
   */
  const calculateTotal = (): number => {
    return cartItems.reduce((acc, item) => acc + item.price * item.quantity, 0);
  };

  /**
   * Validates a Brazilian CNPJ (tax ID).
   * @param {string} cnpj - The CNPJ to validate.
   * @returns {boolean} - Returns true if valid, false otherwise.
   */
  const validateCNPJ = (cnpj: string): boolean => {
    const cleanedCNPJ = cnpj.replace(/[^\d]/g, ''); // Remove non-numeric characters
    return cleanedCNPJ.length === 14;
  };

  /**
   * Validates an email address format.
   * @param {string} email - The email to validate.
   * @returns {boolean} - Returns true if valid, false otherwise.
   */
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
  };

  /**
   * Validates a Brazilian phone number format.
   * @param {string} phone - The phone number to validate.
   * @returns {boolean} - Returns true if valid, false otherwise.
   */
  const validatePhone = (phone: string): boolean => {
    const phoneRegex = /^\+55\d{2}\d{4,5}\d{4}$/; // Matches +55XXXXXXXXXXX format
    return phoneRegex.test(phone);
  };

  const handleEdit = (): void => {
    setTerms([]);
    setActiveTerm(0);
  }

  /**
   * Handles form submission, validating required fields before proceeding.
   */
  const handleSubmit = (): void => {
    let newErrors: FormErrors = {};

    // Validate each input field and set error messages accordingly
    if (!validateCNPJ(formData.cnpj)) newErrors.cnpj = "Invalid CNPJ";
    if (!validateEmail(formData.email)) newErrors.email = "Invalid email";
    if (!validatePhone(formData.phone)) newErrors.phone = "Phone must be in +55XXXXXXXXXXX format";
    if (!formData.firstName.trim()) newErrors.firstName = "First name is required";
    if (!formData.lastName.trim()) newErrors.lastName = "Last name is required";

    // If there are any validation errors, update the state and prevent submission
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    const formDataWithCart = { ...formData };
    formDataWithCart.cart = cartItems;

    // If all validations pass, proceed with form submission
    axios.post(API_BASE_URL + '/buyer/terms/', formDataWithCart)
    .then(response => {
      setTerms(response.data.terms);
    })
    .catch(error => {
      toast.error(error.response.data.message)
    });
  };

  const handleConfirmOrder = (): void => {
    const formDataWithCart = { ...formData };
    formDataWithCart.cart = cartItems;
    formDataWithCart.term = activeTerm;

    // If all validations pass, proceed with form submission
    axios.post(API_BASE_URL + '/order/create/', formDataWithCart)
    .then(response => {
      navigate(`/success/${response.data.credix_order_id}`);
    })
    .catch(error => {
      toast.error(error.response.data.message)
    });
  }

  /**
   * Handles changes to form fields and clears error messages when the user corrects their input.
   * @param {keyof FormData} field - The field being updated.
   * @param {string} value - The new value of the field.
   */
  const handleChange = (field: keyof FormData, value: string): void => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setErrors(prev => ({ ...prev, [field]: '' })); // Clear error on change
  };

  return (
    <div className='credix-checkout'>
      <div className='credix-checkout-left'>
        <div>
          <Card
            title="Company details"
            subtitle="Fill up your company details to get started"
          >
            <TextInput
              disabled={terms.length > 0}
              className="credix-checkout-input" 
              size="small" 
              fullWidth 
              label="CNPJ" 
              variant="outlined" 
              value={formData.cnpj}
              onChange={(e) => handleChange("cnpj", e.target.value)}
              error={!!errors.cnpj}
              helperText={errors.cnpj}
            />
            <TextInput
              disabled={terms.length > 0}
              className="credix-checkout-input" 
              size="small" 
              fullWidth 
              label="Email" 
              variant="outlined" 
              value={formData.email}
              onChange={(e) => handleChange("email", e.target.value)}
              error={!!errors.email}
              helperText={errors.email}
            />
            <TextInput 
              disabled={terms.length > 0}
              className="credix-checkout-input" 
              size="small" 
              fullWidth 
              label="Phone" 
              variant="outlined" 
              value={formData.phone}
              onChange={(e) => handleChange("phone", e.target.value)}
              error={!!errors.phone}
              helperText={errors.phone}
            />
            <TextInput 
              disabled={terms.length > 0}
              className="credix-checkout-input" 
              size="small" 
              fullWidth 
              label="First Name" 
              variant="outlined" 
              value={formData.firstName}
              onChange={(e) => handleChange("firstName", e.target.value)}
              error={!!errors.firstName}
              helperText={errors.firstName}
            />
            <TextInput 
              disabled={terms.length > 0}
              className="credix-checkout-input"
              size="small" 
              fullWidth 
              label="Last Name" 
              variant="outlined" 
              value={formData.lastName}
              onChange={(e) => handleChange("lastName", e.target.value)}
              error={!!errors.lastName}
              helperText={errors.lastName}
            />
            <div className='credix-checkout-action'>
              {terms.length === 0 && <Button onClick={handleSubmit} text="SUBMIT" variant="contained"/>}
              {terms.length > 0 && <Button onClick={handleEdit} text="EDIT" variant="outlined"/>}
            </div>
          </Card>
          {terms.map((term: any) => (
            <Card
              title={'Buy now, Pay later'}
              subtitle={`${term} days term`}
              onClick={() => setActiveTerm(term)}
              headerAction={<Button text="SELECT" variant={ activeTerm === term ? "contained" : "outlined"}/>}
            />
          ))}
        </div>
      </div>
      <div className='credix-checkout-right'>
        <Typography variant="h5">🛒 Your Cart</Typography>
        {cartItems.length === 0 ? (
          <p className="credix-checkout-empty-cart">Your cart is empty! 🛍️</p>
        ) : (
          <div className="credix-checkout-items">
            {cartItems.map((item: CartItem) => (
              <p key={item.sku} className="credix-checkout-item">
                <span className="credix-checkout-item-name">{item.name}</span>
                <span className="credix-checkout-item-quantity">x{item.quantity}</span>
                <span className="credix-checkout-item-price">R${item.price * item.quantity}</span>
              </p>
            ))}
          </div>
        )}
        {cartItems.length > 0 && (
          <div className="credix-checkout-summary">
            {!!activeTerm && <p><strong>Payment term:</strong> {activeTerm} days</p>}
            <p><strong>Subtotal:</strong> R${calculateTotal()}</p>
            <p><strong>Subtotal:</strong> R${calculateTotal()}</p>
            <p><strong>Taxes:</strong> R${Math.round(calculateTotal() * 0.1)}</p>
            <p><strong>Total:</strong> R${calculateTotal() + Math.round(calculateTotal() * 0.1)}</p>
            <Button
              text="CONFIRM ORDER"
              disabled={!activeTerm}
              variant="contained"
              onClick={handleConfirmOrder}
            />
          </div>
        )}
      </div>
      <Toaster />
    </div>
  );
};

export default Checkout;
