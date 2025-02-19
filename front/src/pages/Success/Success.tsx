import { useParams } from "react-router-dom";

const Success = () => {
  const { order_id } = useParams<{ order_id: string }>();

  return (
    <div>
      <h1>Success!</h1>
      <p>Your credix order ID: {order_id}</p>
    </div>
  );
};

export default Success;