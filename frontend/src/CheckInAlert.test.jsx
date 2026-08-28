import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { CheckInAlert } from "./CheckInAlert";

describe("CheckInAlert", () => {
  it("mostra o alerta quando o check-in é antes das 14h", () => {
    render(
      <CheckInAlert message="Check-in permitido a partir das 14h00. O procedimento foi registrado antes do horário previsto." />
    );
    expect(screen.getByText(/14h00/)).toBeInTheDocument();
  });

  it("não renderiza nada sem mensagem", () => {
    const { container } = render(<CheckInAlert message={null} />);
    expect(container).toBeEmptyDOMElement();
  });
});
