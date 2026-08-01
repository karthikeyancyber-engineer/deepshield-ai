import ClientPage from "./ClientPage"

export function generateStaticParams() {
  return [{ token: "placeholder" }]
}

export default function Page() {
  return <ClientPage />
}
