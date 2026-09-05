"""Run with: python -m examples.proportions"""

from humanoid_core import BodyType, HumanoidSpec, generate_proportions


def main() -> None:
    print("Stylized proportions in cm (180 cm, 95 kg)")
    print(f"{'Preset':<12} {'Height':>8} {'Shoulders':>10} {'Waist':>8} {'Hips':>8}")
    for body_type in BodyType:
        spec = HumanoidSpec(height_cm=180, weight_kg=95, body_type=body_type)
        result = generate_proportions(spec)
        print(f"{body_type.value:<12} {result.standing_height_cm:8.1f} "
              f"{result.shoulder_width_cm:10.1f} {result.waist_width_cm:8.1f} "
              f"{result.hip_width_cm:8.1f}")


if __name__ == "__main__":
    main()
