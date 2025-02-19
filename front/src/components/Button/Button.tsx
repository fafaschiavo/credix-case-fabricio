import MuiButton from '@mui/material/Button'; // Renamed import to avoid conflict
import './Button.css';
import { ButtonProps } from '@mui/material/Button';

interface CustomButtonProps extends ButtonProps {
  text: string;
}

const CustomButton: React.FC<CustomButtonProps> = ({ text, ...props }) => {
  return <MuiButton {...props}>{text}</MuiButton>;
};

export default CustomButton;
