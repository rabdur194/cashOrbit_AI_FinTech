import { ShieldCheck } from "lucide-react";
import { Heading } from "../ui";
export function Audit({ events }: { events: any[] }) {
  return (
    <>
      <Heading
        eyebrow="GOVERNANCE"
        title="Audit trail"
        subtitle="Review recent financial actions recorded by CashOrbit."
      />
      <div className="panel">
        <div className="panel-head">
          <div>
            <h2>Recent events</h2>
            <p>Latest 100 organization events</p>
          </div>
          <ShieldCheck size={18} color="#8290a4" />
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Action</th>
                <th>Entity</th>
                <th>Entity ID</th>
                <th>Details</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {events.map((e) => (
                <tr key={e.id}>
                  <td>
                    <strong>{e.action}</strong>
                  </td>
                  <td>{e.entity_type}</td>
                  <td>{e.entity_id ?? "—"}</td>
                  <td
                    style={{
                      maxWidth: 280,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                  >
                    {e.details}
                  </td>
                  <td>{new Date(e.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!events.length && <div className="empty">No audit events.</div>}
        </div>
      </div>
    </>
  );
}
