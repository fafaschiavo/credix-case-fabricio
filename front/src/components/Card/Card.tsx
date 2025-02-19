import * as React from 'react';
import MuiCard, { CardProps as MuiCardProps } from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardHeader from '@mui/material/CardHeader';
import Button from '@mui/material/Button';
import clsx from 'clsx'; // Optional for cleaner class merging
import './Card.css';

// Extend Material-UI's CardProps
interface CardProps extends MuiCardProps {
  title?: string;
  subtitle: string;
  buttonText?: string;
  onButtonClick?: () => void;
  className?: string; // Allow external className
  children?: React.ReactNode;
  headerAction?: React.ReactNode; 
}

const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  buttonText = '',
  onButtonClick,
  className,
  children,
  headerAction,
  ...props
}) => {
  return (
    <MuiCard
      className={clsx('credix-card', className)} // ✅ Merge classes
      sx={{ minWidth: 275 }}
      {...props}
    >
      <CardHeader
        title={title}
        subheader={subtitle}
        action={headerAction}
        className="credix-card-header"
      />
      {children && (
        <CardContent>
          <div className="credix-card-children">{children}</div>
        </CardContent>
      )}
      {buttonText.length > 0 && (
        <CardActions>
          <Button disabled size="small" onClick={onButtonClick}>
            {buttonText}
          </Button>
        </CardActions>
      )}
    </MuiCard>
  );
};

export default Card;
