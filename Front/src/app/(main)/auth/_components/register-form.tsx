"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Controller, useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Field, FieldError, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";

const formSchema = z
  .object({
    name: z.string().min(2, { message: "El nombre es obligatorio." }),
    email: z.string().email({ message: "Ingrese un correo válido." }),
    password: z.string().min(6, { message: "Mínimo 6 caracteres." }),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Las contraseñas no coinciden.",
    path: ["confirmPassword"],
  });

export function RegisterForm() {
  const router = useRouter();
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { name: "", email: "", password: "", confirmPassword: "" },
  });

  const { isSubmitting } = form.formState;

  const onSubmit = async (data: z.infer<typeof formSchema>) => {
    try {
      // URL exacta de tu servidor según el Curl proporcionado
      const response = await fetch("http://10.155.22.8:8000/auth/register", {
        method: "POST",
        headers: {
          "accept": "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: data.name,
          email: data.email,
          password: data.password,
          role: "lector", // Rol fijo según tu documentación
        }),
      });

      const result = await response.json();

      if (response.status === 201) {
        toast.success(result.message); // "Usuario registrado correctamente"
        
        // Opcional: Guardar la llave de Solana si la necesitas después
        // console.log("Solana Key:", result.solana); 

        router.push("/dashboard/metricas");
      } else if (response.status === 422) {
        // Manejo de errores de validación de FastAPI/Pydantic
        toast.error("Error de validación", {
          description: result.detail[0].msg,
        });
      } else {
        throw new Error(result.message || "Error desconocido");
      }
    } catch (error: any) {
      toast.error("Error en el servidor", {
        description: error.message,
      });
    }
  };

  return (
    <form noValidate onSubmit={form.handleSubmit(onSubmit)} className="flex flex-col gap-4">
      <FieldGroup className="gap-4">
        <Controller
          control={form.control}
          name="name"
          render={({ field, fieldState }) => (
            <Field className="gap-1.5" data-invalid={fieldState.invalid}>
              <FieldLabel>Nombre Completo</FieldLabel>
              <Input {...field} placeholder="Tu nombre" disabled={isSubmitting} />
              {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
            </Field>
          )}
        />
        <Controller
          control={form.control}
          name="email"
          render={({ field, fieldState }) => (
            <Field className="gap-1.5" data-invalid={fieldState.invalid}>
              <FieldLabel>Email</FieldLabel>
              <Input {...field} type="email" placeholder="user@example.com" disabled={isSubmitting} />
              {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
            </Field>
          )}
        />
        <Controller
          control={form.control}
          name="password"
          render={({ field, fieldState }) => (
            <Field className="gap-1.5" data-invalid={fieldState.invalid}>
              <FieldLabel>Contraseña</FieldLabel>
              <Input {...field} type="password" placeholder="••••••" disabled={isSubmitting} />
              {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
            </Field>
          )}
        />
        <Controller
          control={form.control}
          name="confirmPassword"
          render={({ field, fieldState }) => (
            <Field className="gap-1.5" data-invalid={fieldState.invalid}>
              <FieldLabel>Confirmar Contraseña</FieldLabel>
              <Input {...field} type="password" placeholder="••••••" disabled={isSubmitting} />
              {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
            </Field>
          )}
        />
      </FieldGroup>
      <Button className="w-full" type="submit" disabled={isSubmitting}>
        {isSubmitting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Registrar"}
      </Button>
    </form>
  );
}