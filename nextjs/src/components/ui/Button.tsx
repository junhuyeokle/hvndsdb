import { cn } from "@/lib/utils";
import styles from "@/styles/components/ui/Button.module.css";
import { cva, type VariantProps } from "class-variance-authority";
import React from "react";

const buttonVariants = cva(styles.button, {
  variants: {
    intent: {
      primary: styles["button--primary"],
      secondary: styles["button--secondary"],
      destructive: styles["button--destructive"],
    },
    tone: {
      solid: styles["button--solid"],
      outline: styles["button--outline"],
      ghost: styles["button--ghost"],
    },
    size: {
      sm: styles["button--sm"],
      md: styles["button--md"],
      lg: styles["button--lg"],
    },
  },
  defaultVariants: {
    intent: "primary",
    tone: "solid",
    size: "md",
  },
});

export type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variantIntent?: VariantProps<typeof buttonVariants>["intent"];
  variantTone?: VariantProps<typeof buttonVariants>["tone"];
  variantSize?: VariantProps<typeof buttonVariants>["size"];
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variantIntent, variantTone, variantSize, ...props }, ref) => {
    const baseClass = buttonVariants({
      intent: variantIntent,
      tone: variantTone,
      size: variantSize,
    });

    return <button ref={ref} className={cn(baseClass, className)} {...props} />;
  }
);

Button.displayName = "Button";
