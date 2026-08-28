export function formatBRL(value) {
  const amount = Number(value);
  return amount.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

export function weekdayLabel(isoDate) {
  const [year, month, day] = isoDate.split("-").map(Number);
  const date = new Date(year, month - 1, day);
  const weekend = date.getDay() === 0 || date.getDay() === 6;
  return weekend ? "fim de semana" : "dia útil";
}
