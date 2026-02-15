from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import SessionLocal 
from app.models.project import Project
from app.models.subject import Subject
from app.models.lesion import Lesion
from app.models.lesion_measurement import LesionMeasurement

SEX = ["M", "F"]
CANCERS = ["NSCLC", "SCLC", "Breast", "CRC", "Melanoma", "Prostate"]
STAGES = ["I", "II", "III", "IV"]
SITES = ["Lung", "Liver", "Brain", "Bone", "Lymph node", "Adrenal"]
LATERALITY = ["Left", "Right", "Midline", None]
MODALITY = ["CT", "MRI", "PET/CT"]
TIMEPOINTS = ["baseline", "week_6", "week_12", "week_18", "week_24"]

def maybe(db: Session, p: float) -> bool:
    return random.random() < p

def seed_db(db: Session,
    n_projects: int = 2,
    subjects_per_project: int = 10,
    lesions_per_subject: int = 3,
    measurements_per_lesion: int = 4,
    clear_first: bool = False,
) -> None:
    if clear_first:
        db.query(LesionMeasurement).delete()
        db.query(Lesion).delete()
        db.query(Subject).delete()
        db.query(Project).delete()
        db.commit()

    now = datetime.now(timezone.utc)

    for p in range(1, n_projects + 1):
        project = Project(
            name=f"Demo Project {p}",
            description="Seeded test data for development",
        )
        db.add(project)
        db.flush()

        for s in range(1, subjects_per_project + 1):
            subject_code = f"S{s:03d}" 
            subject = Subject(
                project_id=project.id,
                subject_code=subject_code,
                sex=random.choice(SEX),
                age_at_diagnosis=random.randint(25, 85),
                cancer_type=random.choice(CANCERS),
                stage=random.choice(STAGES),
            )
            db.add(subject)
            db.flush()

            for l in range(1, lesions_per_subject + 1):
                lesion_label = f"T{l}"
                lesion = Lesion(
                    subject_id=subject.id,
                    lesion_label=lesion_label,
                    anatomic_site=random.choice(SITES),
                    laterality=random.choice(LATERALITY),
                    modality=random.choice(MODALITY),
                )
                db.add(lesion)
                db.flush()

                tps = TIMEPOINTS[:]
                random.shuffle(tps)
                tps = sorted(tps[: min(measurements_per_lesion, len(tps))], key=TIMEPOINTS.index)

                base_long = round(random.uniform(8.0, 60.0), 2)
                base_short = round(base_long * random.uniform(0.4, 0.9), 2)

                for i, tp in enumerate(tps):
                    measured_at = now - timedelta(days=(len(tps) - 1 - i) * 42)

                    drift = random.uniform(-0.15, 0.20)  # -15% to +20% per step
                    long_mm = max(0.0, round(base_long * ((1.0 + drift) ** i), 2))
                    short_mm = max(0.0, round(base_short * ((1.0 + drift) ** i), 2))

                    m = LesionMeasurement(
                        lesion_id=lesion.id,
                        timepoint=tp,
                        measured_at=measured_at,
                        longest_diameter_mm=long_mm,
                        short_axis_mm=short_mm,
                        volume_mm3=round(long_mm * short_mm * random.uniform(50, 120), 2) if maybe(db, 0.4) else None,
                        mean_hu=round(random.uniform(-50, 120), 1) if maybe(db, 0.3) else None,
                        suv_max=round(random.uniform(0.5, 18.0), 2) if maybe(db, 0.3) else None,
                        reviewer=random.choice(["r1", "r2", "r3"]) if maybe(db, 0.8) else None,
                        confidence=round(random.uniform(0.55, 0.99), 2),
                    )
                    db.add(m)

        db.commit()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects", type=int, default=2)
    ap.add_argument("--subjects", type=int, default=10)
    ap.add_argument("--lesions", type=int, default=3)
    ap.add_argument("--measurements", type=int, default=4)
    ap.add_argument("--clear", action="store_true")
    args = ap.parse_args()

    with SessionLocal() as db:
        seed_db(
            db,
            n_projects=args.projects,
            subjects_per_project=args.subjects,
            lesions_per_subject=args.lesions,
            measurements_per_lesion=args.measurements,
            clear_first=args.clear,
        )

    print("✅ Seed complete")


if __name__ == "__main__":
    main()