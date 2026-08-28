export function CheckInAlert({ message }) {
  if (!message) {
    return null;
  }
  return <p className="warn">{message}</p>;
}
