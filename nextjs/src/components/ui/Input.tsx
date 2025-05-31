import { cn } from "@/lib/utils";
import styles from "@/styles/components/ui/Input.module.css";
import { cva, type VariantProps } from "class-variance-authority";
import React from "react";

const inputVariants = cva(styles.input, {
  variants: {
    intent: {
      default: styles["input--default"],
      error: styles["input--error"],
    },
    tone: {
      solid: styles["input--solid"],
      outline: styles["input--outline"],
      ghost: styles["input--ghost"],
    },
    size: {
      sm: styles["input--sm"],
      md: styles["input--md"],
      lg: styles["input--lg"],
    },
  },
  defaultVariants: {
    intent: "default",
    tone: "solid",
    size: "md",
  },
});

export type InputProps = React.InputHTMLAttributes<HTMLInputElement> & {
  variantIntent?: VariantProps<typeof inputVariants>["intent"];
  variantTone?: VariantProps<typeof inputVariants>["tone"];
  variantSize?: VariantProps<typeof inputVariants>["size"];
};

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, variantIntent, variantTone, variantSize, ...props }, ref) => {
    const baseClass = inputVariants({
      intent: variantIntent,
      tone: variantTone,
      size: variantSize,
    });

    return <input ref={ref} className={cn(baseClass, className)} {...props} />;
  }
);

Input.displayName = "Input";
