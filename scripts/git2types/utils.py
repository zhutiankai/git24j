from typing import List
from .git2_type_native import Git2TypeConstString, Git2TypePrimitive
from .git2_type_oid import Git2TypeConstOid, Git2TypeOid
from .git2_type_repository import Git2TypeConstRepository, Git2TypeOutRepository
from .git2_type_strarray import Git2TypeStringArray, Git2TypeOutStringArray
from .git2_type_common import Git2TypeConstIndex

import re


RAW_PAT = re.compile(
    r"\b(?P<type_name>byte|char|short|int|long|float|double)\b")
STRING_PAT = re.compile(r"\b(?P<const>const)?\s*char\s*\*")

GIT2_PARAM_PARSERS = [
    Git2TypeConstString,
    Git2TypePrimitive,
    Git2TypeConstOid,
    Git2TypeOid,
    Git2TypeConstRepository,
    Git2TypeOutRepository,
    Git2TypeOutStringArray,
    Git2TypeStringArray,
    Git2TypeConstIndex,
]


def get_jtype_raw(c_type: str) -> str:
    m = RAW_PAT.match(c_type)
    if not m:
        return ""
    return 'j{}'.format(m.group('type_name'))


def get_jtype_string(c_type: str) -> str:
    m = STRING_PAT.match(c_type)
    if not m:
        return ""
    return "jstring"


def get_jtype(c_type: str) -> str:
    """
    return jni type of c types, e.g:
    int -> jint
    'const char *' -> jstring
    """
    s = c_type.strip()
    return get_jtype_raw(s) or get_jtype_string(s)


def get_return_assign(return_type: str) -> str:
    """
    int foo() => 'int r ='
    void foo() => ''
    """
    s = return_type.strip()
    if 'void' == s:
        return ''
    return '{} r ='.format(s)


def get_return_var(return_type: str) -> str:
    """
    int foo() => return r;
    void foo() => ''
    """
    s = return_type.strip()
    if 'void' == s:
        return ''
    return 'return r;'


def get_git2_param(param: str) -> 'Git2Type':
    for p in GIT2_PARAM_PARSERS:
        t = p.parse(param)
        if t:
            return t
    raise Exception(f"no matching type found for '{param}'")


def get_c_wrapper_param_list(param_list: List['Git2Type']) -> str:
    """
    from: git_oid *out, git_index *index, git_repository *repo
    to: jobject outOid, jlong indexPtr, jlong repoPtr
    """

    return ', '.join([p.c_header_param for p in param_list])


def get_c_param_list(param_list: List['Git2Type']) -> str:
    """
    from: git_oid *out, git_index *index, git_repository *repo
    to: &c_oid, (git_index *)indexPtr, (git_repository *)repoPtr
    """
    return ', '.join([p.c_wrapper_param for p in param_list])


def get_c_wrapper_before_list(param_list: List['Git2Type']) -> str:
    """
    from: git_oid *out, git_index *index, git_repository *repo
    to: 'git_oid c_oid;'
    """
    return ''.join([p.c_wrapper_before for p in param_list])


def get_c_wrapper_after_list(param_list: List['Git2Type']) -> str:
    """
    from: git_oid *out, git_index *index, git_repository *repo
    to: 'git_oid c_oid;'
    """
    return ''.join([p.c_wrapper_after for p in param_list])


def get_jni_param_list(param_list: List['Git2Type']) -> str:
    """
    from: git_oid *out, git_index *index, git_repository *repo
    to: Oid out, long indexPtr, long repoPtr
    """
    return ', '.join([p.jni_param for p in param_list])