import { formatBRL, weekdayLabel } from "./money";

export function CheckoutSummary({ bill }) {
  if (!bill) {
    return null;
  }

  return (
    <section className="bill">
      <h3>Total da reserva</h3>
      <table>
        <thead>
          <tr>
            <th>Data</th>
            <th>Tipo</th>
            <th>Diária</th>
            <th>Estacionamento</th>
            <th>Subtotal</th>
          </tr>
        </thead>
        <tbody>
          {bill.items.map((item) => (
            <tr key={item.date}>
              <td>{item.date}</td>
              <td>{weekdayLabel(item.date)}</td>
              <td>{formatBRL(item.daily)}</td>
              <td>{formatBRL(item.parking)}</td>
              <td>{formatBRL(item.subtotal)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p>Taxa de check-out tardio: {formatBRL(bill.late_checkout_fee)}</p>
      <p className="total">
        <strong>Total geral: {formatBRL(bill.total)}</strong>
      </p>
    </section>
  );
}
