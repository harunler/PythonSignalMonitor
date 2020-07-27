from ipywidgets import HBox, VBox, Layout, Label, Checkbox, interactive as i_active, Output, HTML, fixed as fix
from IPython.display import display
import plotly
import plotly.graph_objs as go
from datetime import timedelta, datetime as dt

# Must enable in order to use plotly off-line (or in cloud)
plotly.offline.init_notebook_mode()

CLR_NONE: str = "rgba(0,0,0,0)"
CLR_GRAPH_BG: str = "white"
CLR_SIGNAL: str = "navy"
CLR_OP_LIM: str = "red"
CLR_OP_TOL: str = "orange"
CLR_OP_DEF: str = "green"
CLR_GRAPH_GRD: str = "rgba(176,196,222,0.2)" #"rgba(176,196,222,0.2)" #"rgba(0,0,0,0.2)" #"rgba(249,231,159,0.8)"
SYM_CURRENT: str = "star-diamond"
DEF_TITLE:str = "Signal Operation Monitor"
DEF_FONT_FAM: str = "Arial"
DEF_FONT_SIZE: int = 12
DEF_FONT_CLR: str = "#000000"
DEF_Y_MIN: float = 0.0
DEF_Y_MAX: float = 100.0
DEF_MARGIN: str = "10px"
DEF_TICK_TIME_DELTA = timedelta(seconds=1)
TIT_MARGIN: str = f"margin:{DEF_MARGIN}"
SUB_TIT_MARGIN: str = "margin:3px 2px 1px 20px"
LBL_MARGIN: str = f"margin:0px 3px 0px 30px"
TXT_CURRENT: str = "Current"
TXT_LOCAL: str = "Local"
TXT_SIGNAL: str = "Signal"
TXT_LIM: str = "Limit"
TXT_TOL: str = "Tolerance"
TXT_LIM_MAX: str = "Limit max"
TXT_LIM_MIN: str = "Limit min"
TXT_TOL_MIN: str = "Tol. min"
TXT_TOL_MAX: str = "Tol. max"
TXT_OP_RANGE: str = "Operation Range"
OUT_LAYOUT = dict(border=f"2px solid {CLR_GRAPH_GRD}", width="auto", height="auto")
LIN_LIM_MIN = dict(color=CLR_OP_LIM, dash="dot", width=1)
LIN_LIM_MAX = dict(color=CLR_OP_LIM, dash="dash", width=1)
LIN_TOL_MIN = dict(color=CLR_OP_TOL, dash="dot", width=1)
LIN_TOL_MAX = dict(color=CLR_OP_TOL, dash="dash", width=1)
MRK_SIGNAL = dict(color="navy", size=3)
GRA_OUT_LAYOUT = dict(border="none", width="auto", height="auto")
GRA_LAYOUT = go.Layout(height=400, paper_bgcolor=CLR_NONE, plot_bgcolor=CLR_GRAPH_BG, showlegend=True,
                       margin=go.layout.Margin(l=60, r=20, t=20, b=20),
                       font=dict(family=DEF_FONT_FAM, size=DEF_FONT_SIZE, color=DEF_FONT_CLR),
                       xaxis=dict(zeroline=False, zerolinewidth=1, zerolinecolor=CLR_GRAPH_GRD,
                                    showgrid=True, gridwidth=0.4, gridcolor=CLR_GRAPH_GRD,
                                    ticks="outside", ticklen=5, tickangle=45, tickcolor=CLR_GRAPH_GRD, type="date"),
                       yaxis=dict(zeroline=False, zerolinewidth=1, zerolinecolor=CLR_GRAPH_GRD,
                                    showgrid=True, gridwidth=0.4, gridcolor=CLR_GRAPH_GRD,
                                    ticks="outside", ticklen=5, tickangle=0, tickcolor=CLR_GRAPH_GRD))
OUT_STYLE: str = "<style>" \
                    ".mon-out { " + \
                        f"background-color:{CLR_GRAPH_GRD} !important;" + \
                    "}" \
                    ".v-sig { " + \
                        f"color:{CLR_SIGNAL} !important" + \
                    "}" \
                    ".v-def { " + \
                        f"color:{CLR_OP_DEF} !important" + \
                    "}" \
                    ".v-tol { " + \
                        f"color:{CLR_OP_TOL} !important" + \
                    "}" \
                    ".v-lim { " + \
                        f"color:{CLR_OP_LIM} !important" + \
                    "}" \
                    ".bold { " \
                        "font-weight:bold" \
                    "}" \
                    ".mon-val-y { " \
                        "font-size:28px;" \
                        "font-weight:bold;" \
                        "margin:0px 3px 0px 30px" \
                    "}" \
                    ".mon-val-x { " \
                        "font-size:16px;" \
                        "margin:50px 3px 0px 30px" \
                    "}" \
                    ".mon-val-x2 { " \
                        "font-size:16px;" \
                        "margin:4px 3px 0px 30px" \
                    "}" \
                "</style>"

class MonitorV2:
    _data: list
    _op_lim_max = None
    _op_lim_min = None
    _op_tol_max = None
    _op_tol_min = None
    _y_unit: str
    _x_unit: str
    _max_plots: int
    _x_pre_tick: timedelta
    _x_post_tick: timedelta
    _plot_trigger: Checkbox
    _graph: i_active
    _curr: i_active
    _out: Output
    _group: VBox
    _graph_layout: go.Layout

    def __init__(self, title=DEF_TITLE, y_unit="%", x_unit="utc", max_plots=5, data=None, y_min=DEF_Y_MIN,
                 y_max=DEF_Y_MAX, x_pre_tick=None, x_post_tick=None, op_enabled=False, op_lim_min=None,
                 op_lim_max=None, op_tol_min=None, op_tol_max=None):

        ti, oe, xu, yu, pt = (title, op_enabled, x_unit, y_unit, Checkbox(value=False))
        pt.layout.visibility = 'hidden'
        yl, yh = (DEF_Y_MIN if y_min is None else y_min, DEF_Y_MAX if y_max is None else y_max)
        mp, oll, olh = (max_plots, op_lim_min if oe else None, op_lim_max if oe else None)
        to = 0 if not oe else olh - oll if oll and olh else yh - oll if olh is None else olh - yl if oll is None else 0
        oth = MonitorV2._get_tolerance(oe, op_tol_max, olh, to)
        otl = MonitorV2._get_tolerance(oe, op_tol_min, oll, -to)
        ic = i_active(self.show_current, t=pt, e=fix(oe), l=fix(oll), h=fix(olh), i=fix(otl), j=fix(oth))
        ig = i_active(self.show_graph, t=pt, e=fix(oe), l=fix(oll), h=fix(olh), i=fix(otl), j=fix(oth))
        self._out = Output(layout=OUT_LAYOUT)
        self._out.add_class("mon-out")
        og = ig.children[-1]
        og.layout = GRA_OUT_LAYOUT
        d_oll = f"{oll:.2f}" if oe and oll is not None else "None"
        d_olh = f"{olh:.2f}" if oe and olh is not None else "None"
        d_otl = f"{otl:.2f}" if oe and otl is not None else "None"
        d_oth = f"{oth:.2f}" if oe and oth is not None else "None"
        vb = VBox([HTML(OUT_STYLE), Label(layout=Layout(width='350px')), HTML(f"<h2 style='{TIT_MARGIN}'>{ti}</h2>"),
                   HTML(f"<h3 style='{SUB_TIT_MARGIN}'>{TXT_OP_RANGE} {'(on)' if oe else '(off)'}</h3>"),
                   HBox([HTML(f"<h4 style='{LBL_MARGIN}'>{TXT_LIM}</h4>"),
                         Label(f"min: {d_oll}, max: {d_olh} {yu if oll is not None or d_olh is not None else ''}")]),
                   HBox([HTML(f"<h4 style='{LBL_MARGIN}'>{TXT_TOL}:</h4>"),
                         Label(f"min: {d_otl}, max: {d_oth} {yu if d_otl is not None or d_oth is not None else ''}")]),
                   HTML(f"<h3 style='{SUB_TIT_MARGIN}'>{TXT_CURRENT}</h3>"), ic
                   ])
        hb = HBox([vb, ig])
        self._group = VBox([hb])
        self._graph_layout = GRA_LAYOUT
        self._graph_layout.update(dict(xaxis_title=xu, yaxis_title=yu))
        self._graph_layout.yaxis.update(range=[yl, yh])
        self._graph_layout.update(xaxis_tickformat="%H:%M:%S")
        self._x_pre_tick = x_pre_tick if x_pre_tick is not None else DEF_TICK_TIME_DELTA
        self._x_post_tick = x_post_tick if x_post_tick is not None else DEF_TICK_TIME_DELTA
        self._data = [[],[]]
        if data is not None:
            dx = data[0]
            dy = data[1]
            self._data = [dx, dy]
        self._x_unit, self._y_unit, self._plot_trigger, self._max_plots, self._graph = (xu, yu, pt, mp, ig)
        self._op_lim_min, self._op_lim_max, self._op_tol_min, self._op_tol_max, self._Curr = (oll, olh, otl, oth, ic)

    @staticmethod
    def _get_tolerance(enabled, t_v, l_v, total):
        if not enabled or t_v is None or l_v is None or not total: return None
        return l_v - (total * float(str(t_v).replace("%", "")) / 100.0 if str(t_v).endswith("%") else l_v -  float(t_v))

    def show_current(self, t, e, l, h, i, j):
        if t is None: return
        vd = self._data
        if not vd[1]: return
        xv, yv, vs, vd, vt, vl = (vd[0][len(vd[0]) - 1], vd[1][len(vd[1]) - 1], "v-sig", "v-def", "v-tol", "v-lim")
        cls = vs if not e else vl if h is not None and yv > h or l is not None and yv < l else vt if \
            i is not None and yv < i or j is not None and yv > j else vd
        v = f"<div class='mon-val-y {cls}'><span>{yv:.3f} {self._y_unit}</span></div>"
        t1 = str(xv.isoformat(timespec='seconds')).replace('T', ' ')
        td = dt.now() - dt.utcnow()
        t2 = str((xv + timedelta(seconds=td.seconds)).isoformat(timespec='seconds')).replace('T', ' ')
        ts = f"<div class='mon-val-x'><span class='bold'>{self._x_unit.capitalize()}</span><span>: {t1}</span></div>"
        tl = f"<div class='mon-val-x2'><span class='bold'>{TXT_LOCAL.capitalize()}</span><span>: {t2}</span></div>"
        display(HTML(v + ts + tl))

    def show_graph(self, t, e, l, h, i, j):
        if t is None: return
        gd = self._data
        x_data = gd[0][len(gd[0]) - self._max_plots:]
        y_data = gd[1][len(gd[1]) - self._max_plots:] if gd[1] and len(gd[1]) > self._max_plots else gd[1]
        config = {"displayModeBar": False}
        fig = go.Figure(layout=self._graph_layout)
        fig.update_yaxes(nticks=10)
        x_min = x_data[0] - self._x_pre_tick
        x_max = x_data[len(x_data) - 1] + self._x_post_tick
        fig.update_xaxes(range=[x_min, x_max])
        if y_data and len(y_data):
            if e:
                opc = 0.6
                if h:
                    x_l_max, y_l_max, tlh, llh = ([x_min, x_max], [h, h], TXT_LIM_MAX, LIN_LIM_MAX)
                    fig.add_trace(go.Scatter(x=x_l_max, y=y_l_max, mode="lines", name=tlh, line=llh, opacity=opc))
                if l:
                    x_l_min, y_l_min, tll, lll = ([x_min, x_max], [l, l], TXT_LIM_MIN, LIN_LIM_MIN)
                    fig.add_trace(go.Scatter(x=x_l_min, y=y_l_min, mode="lines", name=tll, line=lll, opacity=opc))
                if j:
                    x_t_max, y_t_max, tth, lth = ([x_min, x_max], [j, j], TXT_TOL_MAX, LIN_TOL_MAX)
                    fig.add_trace(go.Scatter(x=x_t_max, y=y_t_max, mode="lines", name=tth, line=lth, opacity=opc))
                if i:
                    x_t_min, y_t_min, ttl, ltl = ([x_min, x_max], [i, i], TXT_TOL_MIN, LIN_TOL_MIN)
                    fig.add_trace(go.Scatter(x=x_t_min, y=y_t_min, mode="lines", name=ttl, line=ltl, opacity=opc))
            y_len = len(y_data)
            x_plot = x_data[len(x_data) - y_len:]
            fig.add_trace(go.Scatter(x=x_plot, y=y_data, mode="markers", name=TXT_SIGNAL, marker=MRK_SIGNAL,
                                     opacity=0.6))
            x_cur, y_cur = ([x_data[len(x_data) - 1]], [y_data[len(y_data) - 1]])
            yv, cs, cd, ct, cl = (y_cur[0], CLR_SIGNAL, CLR_OP_DEF, CLR_OP_TOL, CLR_OP_LIM)
            m_clr = cs if not e else cl if h is not None and yv > h or l is not None and yv < l else ct if \
                i is not None and yv < i or j is not None and yv > j else cd
            m_cur = dict(color=m_clr, size=12, symbol=SYM_CURRENT)
            fig.add_trace(go.Scatter(x=x_cur, y=y_cur, mode="markers", name=TXT_CURRENT, opacity=1.0, marker=m_cur))
        fig.show(config=config)

    def _plot_graph(self):
        self._plot_trigger.value = True if not self._plot_trigger.value else False

    def update(self, x, y):
        x_data, y_data = self._data
        x_data.append(x)
        y_data.append(y)
        self._plot_graph()

    def output(self):
        with self._out: display(self._group)
        return self._out