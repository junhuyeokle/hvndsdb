import { Button, ButtonProps } from "@/components/ui/Button";
import { cn } from "@/lib/utils";
import styles from "@/styles/components/custom/IconButton.module.css";
import { cva, type VariantProps } from "class-variance-authority";
import React from "react";

const iconButtonVariants = cva(styles.iconButton, {
  variants: {
    shape: {
      circle: styles["iconButton--circle"],
      square: styles["iconButton--square"],
    },
    emphasis: {
      subtle: styles["iconButton--subtle"],
      strong: styles["iconButton--strong"],
    },
    size: {
      sm: styles["iconButton--sm"],
      md: styles["iconButton--md"],
      lg: styles["iconButton--lg"],
    },
  },
  defaultVariants: {
    shape: "circle",
    emphasis: "subtle",
    size: "md",
  },
});

type IconButtonVariantProps = {
  variantShape?: VariantProps<typeof iconButtonVariants>["shape"];
  variantEmphasis?: VariantProps<typeof iconButtonVariants>["emphasis"];
};

type IconButtonProps = Omit<ButtonProps, "children"> &
  IconButtonVariantProps & {
    icon: React.ReactElement;
    "aria-label": string;
    title: string;
    variantIntent?: ButtonProps["variantIntent"];
    variantTone?: ButtonProps["variantTone"];
    variantSize?: ButtonProps["variantSize"];
  };

export const IconButton = React.forwardRef<HTMLButtonElement, IconButtonProps>(
  (
    {
      className,
      icon,
      variantIntent,
      variantTone,
      variantSize,
      variantShape,
      variantEmphasis,
      variantSize: variantIconSize,
      "aria-label": ariaLabel,
      title,
      ...props
    },
    ref
  ) => {
    const iconClass = iconButtonVariants({
      shape: variantShape,
      emphasis: variantEmphasis,
      size: variantIconSize,
    });

    return (
      <Button
        ref={ref}
        variantIntent={variantIntent}
        variantTone={variantTone}
        variantSize={variantSize ?? variantIconSize}
        {...props}
        className={cn(iconClass, className)}
        aria-label={ariaLabel}
        title={title}
      >
        {icon}
      </Button>
    );
  }
);

IconButton.displayName = "IconButton";
