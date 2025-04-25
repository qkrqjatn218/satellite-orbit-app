import orbit_determination # (사용 여부 미확인, 아마 SGP4 보조)
from orbit_determination.alpha5 import from_alpha5 # 위성 번호 변환
from orbit_determination.earth_gravity import wgs72old, wgs72, wgs84 # 중력 모델 상수
from orbit_determination.ext import invjday, jday # 율리우스일 변환
from orbit_determination.io import twoline2rv  # TLE 해석
from orbit_determination.propagation import sgp4, sgp4init  # SGP4 본체 전파 알고리즘

"""
graph TD
  A[시작: TLE 문자열 2줄] --> B[twoline2rv 호출]
  B --> C[Satrec 객체 초기화]
  C --> D[SGP4init 내부 호출로 orbital elements 설정]
  D --> E[jdsatepoch, epochdays 계산]
  E --> F[전파 호출: sgp4(jd, fr) or sgp4_tsince(t)]
  F --> G[전파결과: 위치 r, 속도 v, 에러코드 반환]

  subgraph 다중 위성 전파 (SatrecArray)
    H[여러 Satrec 객체 리스트] --> I[sgp4(jd, fr) 루프 호출]
    I --> J[모든 r,v 결과 배열화]
  end

"""

WGS72OLD = 0
WGS72 = 1
WGS84 = 2
gravity_constants = wgs72old, wgs72, wgs84
minutes_per_day = 1440.

class Satrec(object):
    
    __slots__ = (
        'Om', 'a', 'alta', 'altp', 'am', 'argpdot', 'argpo', 'atime', 'aycof',
        'bstar', 'cc1', 'cc4', 'cc5', 'classification', 'con41', 'd2', 'd2201',
        'd2211', 'd3', 'd3210', 'd3222', 'd4', 'd4410', 'd4422', 'd5220',
        'd5232', 'd5421', 'd5433', 'dedt', 'del1', 'del2', 'del3', 'delmo',
        'didt', 'dmdt', 'dnodt', 'domdt', 'e3', 'ecco', 'ee2', 'elnum', 'em',
        'ephtype', 'epoch', 'epochdays', 'epochyr', 'error', 'error_message',
        'eta', 'gsto', 'im', 'inclo', 'init', 'intldesg', 'irez', 'isimp',
        'j2', 'j3', 'j3oj2', 'j4', 'jdsatepoch', 'mdot', 'method', 'mm', 'mo',
        'mu', 'nddot', 'ndot', 'nm', 'no_kozai', 'no_unkozai', 'nodecf',
        'nodedot', 'nodeo', 'om', 'omgcof', 'operationmode', 'peo', 'pgho',
        'pho', 'pinco', 'plo', 'radiusearthkm', 'revnum', 'satnum_str', 'se2',
        'se3', 'sgh2', 'sgh3', 'sgh4', 'sh2', 'sh3', 'si2', 'si3', 'sinmao',
        'sl2', 'sl3', 'sl4', 't', 't2cof', 't3cof', 't4cof', 't5cof', 'tumin',
        'x1mth2', 'x7thm1', 'xfact', 'xgh2', 'xgh3', 'xgh4',
        'xh2', 'xh3', 'xi2', 'xi3', 'xke', 'xl2', 'xl3', 'xl4', 'xlamo',
        'xlcof', 'xli', 'xmcof', 'xni', 'zmol', 'zmos',
        'jdsatepochF'
    )

    array = None

    @property
    def no(self):
        return self.no_kozai

    @property
    def satnum(self):
        return from_alpha5(self.satnum_str)

    @classmethod
    # TLE 데이터를 받아 Satrec 객체로 초기화
    def twoline2rv(cls, line1, line2, whichconst=WGS72):
        whichconst = gravity_constants[whichconst]
        self = cls()
        twoline2rv(line1, line2, whichconst, 'i', self)

        self.ephtype = int(self.ephtype.strip() or '0')
        self.revnum = int(self.revnum)

        year = self.epochyr
        days, fraction = divmod(self.epochdays, 1.0)
        self.jdsatepoch = year * 365 + (year - 1) // 4 + days + 1721044.5
        self.jdsatepochF = round(fraction, 8)

        del self.epoch

        self.epochyr %= 100
        return self

    # 사용자 정의 orbital elements로 초기화
    def sgp4init(self, whichconst, opsmode, satnum, epoch, bstar,
                 ndot, nddot, ecco, argpo, inclo, mo, no_kozai, nodeo):
        whichconst = gravity_constants[whichconst]
        whole, fraction = divmod(epoch, 1.0)
        whole_jd = whole + 2433281.5

        if round(epoch, 8) == epoch:
            fraction = round(fraction, 8)

        self.jdsatepoch = whole_jd
        self.jdsatepochF = fraction

        y, m, d, H, M, S = invjday(whole_jd)
        jan0 = jday(y, 1, 0, 0, 0, 0.0)
        self.epochyr = y % 100
        self.epochdays = whole_jd - jan0 + fraction

        self.classification = 'U'

        sgp4init(whichconst, opsmode, satnum, epoch, bstar, ndot, nddot,
                 ecco, argpo, inclo, mo, no_kozai, nodeo, self)

    # 특정 율리우스 날짜에서 r, v 전파
    def sgp4(self, jd, fr):
        tsince = ((jd - self.jdsatepoch) * minutes_per_day +
                  (fr - self.jdsatepochF) * minutes_per_day)
        r, v = sgp4(self, tsince)
        return self.error, r, v
    
    # epoch 이후 tsince (minutes) 기준 전파
    def sgp4_tsince(self, tsince):
        r, v = sgp4(self, tsince)
        return self.error, r, v

    # 특정 시간 간격으로 r,v 값을 numpy array 로 표현#
    def sgp4_array(self, jd, fr):
        
        array = self.array
        if array is None:
            from numpy import array
            Satrec.array = array

        results = []
        z = list(zip(jd, fr))
        for jd_i, fr_i in z:
            results.append(self.sgp4(jd_i, fr_i))
        elist, rlist, vlist = zip(*results)

        e = array(elist)
        r = array(rlist)
        v = array(vlist)

        r.shape = v.shape = len(jd), 3
        return e, r, v


# 복수 위성에 대한 전파 처리
class SatrecArray(object):
    
    __slots__ = ('_satrecs',)

    array = None

    def __init__(self, satrecs):
        self._satrecs = satrecs
        
        if self.array is None:
            from numpy import array
            SatrecArray.array = array

    def sgp4(self, jd, fr):
        
        results = []
        z = list(zip(jd, fr))
        for satrec in self._satrecs:
            for jd_i, fr_i in z:
                results.append(satrec.sgp4(jd_i, fr_i))
        elist, rlist, vlist = zip(*results)

        e = self.array(elist)
        r = self.array(rlist)
        v = self.array(vlist)

        jdlen = len(jd)
        mylen = len(self._satrecs)
        e.shape = (mylen, jdlen)
        r.shape = v.shape = (mylen, jdlen, 3) 

        return e, r, v

# 구버전 호환용(이전 버전(sgp4 1.x)과의 호환성 유지용 레거시 클래스입니다)
class Satellite(object):
    """The old Satellite object, for compatibility with sgp4 1.x."""
    jdsatepochF = 0.0  # for compatibility with new Satrec; makes tests simpler

    def propagate(self, year, month=1, day=1, hour=0, minute=0, second=0.0):
        """Return a position and velocity vector for a given date and time."""

        j = jday(year, month, day, hour, minute, second)
        m = (j - self.jdsatepoch) * minutes_per_day
        r, v = sgp4(self, m)
        return r, v

    no = Satrec.no
    satnum = Satrec.satnum
