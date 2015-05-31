<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="html" indent="yes"/>
  
  <xsl:template match="/results/*">
  
    <TABLE BORDER="1"> 
        <CAPTION> Results for function : <xsl:value-of select="name(.)"/> </CAPTION> 
        <TR> 
            <TH> Test </TH>
            <TH> Breakpoint </TH> 
            <TH> Test result </TH> 
            <TH> FI Result </TH> 
        </TR>
        <xsl:for-each select="*">
            <xsl:variable name="testName" select="name(.)" /> 
            <xsl:for-each select="*">
                <TR>    
                    <th><xsl:copy-of select="$testName"/></th>
                    <td><xsl:value-of select="breakpointHit"/></td>
                    <td><xsl:value-of select="returnCode"/></td>
                    <xsl:choose>
                    <xsl:when test="FIResult='FI detected'">
                        <th bgcolor="#33CC33"><xsl:copy-of select="FIResult"/></th>
                    </xsl:when>
                    <xsl:when test="FIResult = 'Failed'">
                        <th bgcolor="#FF0000"><xsl:copy-of select="FIResult"/></th>
                    </xsl:when>
                    <xsl:when test="FIResult = 'No injection'">
                        <th bgcolor="#FFA500"><xsl:copy-of select="FIResult"/></th>
                    </xsl:when>
                    <xsl:otherwise>
                        <th bgcolor="#FFFF00"><xsl:copy-of select="FIResult"/></th>
                    </xsl:otherwise>
                </xsl:choose>
                </TR>
            </xsl:for-each>
        </xsl:for-each>
    </TABLE>
    
  </xsl:template>
  
</xsl:stylesheet>
