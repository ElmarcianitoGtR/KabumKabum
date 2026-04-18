"use client"; // Si prefieres manejarlo desde el cliente por ahora

export async function registerUser(formData: any) {
  try {
    const response = await fetch("http://10.155.22.8:8000/auth/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Error al registrar usuario");
    }

    return { success: true, data };
  } catch (error: any) {
    return { success: false, error: error.message };
  }
}