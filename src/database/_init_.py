from typing import Optional, Dict, Any, List
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import json

Base = declarative_base()


class ParsedResumeORM(Base):
    __tablename__ = "resumes"

    id = sa.Column(sa.String, primary_key=True)
    filename = sa.Column(sa.String)
    path = sa.Column(sa.String)
    raw_text = sa.Column(sa.Text)
    parsed_json = sa.Column(sa.Text)


class ParsedResume:
    def __init__(self, id: str, filename: str, path: str, raw_text: str, parsed: Dict[str, Any]):
        self.id = id
        self.filename = filename
        self.path = path
        self.raw_text = raw_text
        self.parsed = parsed

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "path": self.path,
            "raw_text": self.raw_text,
            "parsed": self.parsed
        }


class Database:
    def __init__(self, url: str = "sqlite:///./resumes.db"):
        self.engine = sa.create_engine(
            url, connect_args={"check_same_thread": False}
        )
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)

    def save_resume(self, resume: ParsedResume):
        session = self.Session()
        try:
            row = ParsedResumeORM(
                id=resume.id,
                filename=resume.filename,
                path=resume.path,
                raw_text=resume.raw_text,
                parsed_json=json.dumps(resume.parsed, default=str)
            )
            session.merge(row)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_resume(self, id: str) -> Optional[ParsedResume]:
        session = self.Session()
        try:
            row = session.query(ParsedResumeORM).filter_by(id=id).first()
            
            if not row:
                return None

            return ParsedResume(
                id=row.id,
                filename=row.filename,
                path=row.path,
                raw_text=row.raw_text,
                parsed=json.loads(row.parsed_json)
            )
        finally:
            session.close()

    def search_by_text(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        session = self.Session()
        try:
            rows = (
                session.query(ParsedResumeORM)
                .filter(ParsedResumeORM.raw_text.ilike(f"%{query}%"))
                .limit(limit)
                .all()
            )
            return [{"id": r.id, "filename": r.filename} for r in rows]
        finally:
            session.close()