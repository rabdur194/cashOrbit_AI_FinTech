const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export function getToken(){ if(typeof window === "undefined") return ""; return localStorage.getItem("cashorbit_token") || ""; }
export function setToken(token:string){ localStorage.setItem("cashorbit_token",token); }
export function clearToken(){ localStorage.removeItem("cashorbit_token"); }
export async function api<T=any>(path:string, options:RequestInit = {}):Promise<T>{
  const token=getToken(); const headers:Record<string,string>={...(options.headers as Record<string,string>||{})};
  if(token) headers.Authorization=`Bearer ${token}`;
  if(options.body && !(options.body instanceof FormData)) headers["Content-Type"]="application/json";
  const response=await fetch(`${API_URL}${path}`,{...options,headers,cache:"no-store"});
  if(!response.ok){ const body=await response.json().catch(()=>({})); if(response.status===401 && typeof window!=="undefined"){clearToken();} throw new Error(body.detail || `Request failed (${response.status})`); }
  return response.json();
}
export function money(minor:number,currency="BDT"){return new Intl.NumberFormat("en-BD",{style:"currency",currency,maximumFractionDigits:2}).format(minor/100);}
