from dataclasses import dataclass, field


@dataclass
class Record:
    course_code: str
    course_title: str
    branch: str
    semester: int
    l_t_p_credits: dict
    modules: list = field(default_factory=list)